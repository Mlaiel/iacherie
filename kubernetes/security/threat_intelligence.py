"""
Advanced Cyber Threat Intelligence System

Provides real-time threat intelligence gathering, analysis, and sharing
capabilities for the IA Influencer Agent platform deployment security.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""

import asyncio
import logging
import json
import hashlib
import time
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import redis.asyncio as aioredis
import ipaddress
import dns.resolver
import ssl
import socket

logger = logging.getLogger(__name__)


class ThreatIntelligenceSource(Enum):
    """Threat intelligence sources"""
    VIRUSTOTAL = "virustotal"
    ALIENVAULT_OTX = "alienvault_otx"
    MISP = "misp"
    THREATFOX = "threatfox"
    ABUSE_CH = "abuse_ch"
    SHODAN = "shodan"
    GREYNOISE = "greynoise"
    INTERNAL = "internal"
    OSINT = "osint"


class IndicatorType(Enum):
    """Types of threat indicators"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    CERTIFICATE = "certificate"
    USER_AGENT = "user_agent"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    CVE = "cve"


class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    C2_SERVER = "c2_server"
    BOTNET = "botnet"
    EXPLOITATION = "exploitation"
    SUSPICIOUS = "suspicious"
    SCANNING = "scanning"
    SPAM = "spam"
    APT = "apt"
    RANSOMWARE = "ransomware"


class ConfidenceLevel(Enum):
    """Confidence levels for threat intelligence"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ThreatIndicator:
    """Threat intelligence indicator"""
    indicator_id: str
    indicator_type: IndicatorType
    indicator_value: str
    threat_types: List[ThreatType]
    confidence: ConfidenceLevel
    source: ThreatIntelligenceSource
    first_seen: datetime
    last_seen: datetime
    description: str
    tags: Set[str] = field(default_factory=set)
    context: Dict[str, Any] = field(default_factory=dict)
    ttl: int = 86400  # Time to live in seconds
    is_active: bool = True


@dataclass
class ThreatCampaign:
    """Threat campaign information"""
    campaign_id: str
    name: str
    description: str
    threat_actor: str
    tactics: List[str]
    techniques: List[str]
    indicators: List[str]  # Indicator IDs
    first_seen: datetime
    last_activity: datetime
    target_sectors: List[str]
    target_countries: List[str]
    severity: str


@dataclass
class ThreatActor:
    """Threat actor profile"""
    actor_id: str
    name: str
    aliases: List[str]
    description: str
    motivation: str
    origin_country: Optional[str]
    target_sectors: List[str]
    techniques: List[str]
    campaigns: List[str]  # Campaign IDs
    first_seen: datetime
    last_activity: datetime


class VirusTotalClient:
    """
    VirusTotal API client for threat intelligence
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/vtapi/v2"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def lookup_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Lookup IP address reputation
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            VirusTotal IP report
        """



        try:
            url = f"{self.base_url}/ip-address/report"
            params = {
                'apikey': self.api_key,
                'ip': ip_address
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"VirusTotal API error for IP {ip_address}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to lookup IP {ip_address}: {e}")
            return {}
    
    async def lookup_domain(self, domain: str) -> Dict[str, Any]:
        """
        Lookup domain reputation
        
        Args:
            domain: Domain to lookup
            
        Returns:
            VirusTotal domain report
        """



        try:
            url = f"{self.base_url}/domain/report"
            params = {
                'apikey': self.api_key,
                'domain': domain
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"VirusTotal API error for domain {domain}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to lookup domain {domain}: {e}")
            return {}
    
    async def lookup_url(self, url: str) -> Dict[str, Any]:
        """
        Lookup URL reputation
        
        Args:
            url: URL to lookup
            
        Returns:
            VirusTotal URL report
        """



        try:
            api_url = f"{self.base_url}/url/report"
            params = {
                'apikey': self.api_key,
                'resource': url
            }
            
            async with self.session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"VirusTotal API error for URL {url}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to lookup URL {url}: {e}")
            return {}
    
    async def lookup_file_hash(self, file_hash: str) -> Dict[str, Any]:
        """
        Lookup file hash reputation
        
        Args:
            file_hash: File hash to lookup
            
        Returns:
            VirusTotal file report
        """



        try:
            url = f"{self.base_url}/file/report"
            params = {
                'apikey': self.api_key,
                'resource': file_hash
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"VirusTotal API error for hash {file_hash}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to lookup hash {file_hash}: {e}")
            return {}


class AlienVaultOTXClient:
    """
    AlienVault OTX (Open Threat Exchange) client
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'X-OTX-API-KEY': self.api_key}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def lookup_ip(self, ip_address: str) -> Dict[str, Any]:
        """Lookup IP in OTX"""



        try:
            url = f"{self.base_url}/indicators/IPv4/{ip_address}/general"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"OTX IP lookup failed: {e}")
            return {}
    
    async def lookup_domain(self, domain: str) -> Dict[str, Any]:
        """Lookup domain in OTX"""



        try:
            url = f"{self.base_url}/indicators/domain/{domain}/general"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"OTX domain lookup failed: {e}")
            return {}
    
    async def get_pulses(self, modified_since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get recent threat intelligence pulses"""



        try:
            url = f"{self.base_url}/pulses/subscribed"
            params = {}
            
            if modified_since:
                params['modified_since'] = modified_since.isoformat()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"OTX pulses lookup failed: {e}")
            return []


class ThreatIntelligenceDatabase:
    """
    Local threat intelligence database with caching and aggregation
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        
        # In-memory cache for fast lookups
        self.indicators_cache: Dict[str, ThreatIndicator] = {}
        self.campaigns_cache: Dict[str, ThreatCampaign] = {}
        self.actors_cache: Dict[str, ThreatActor] = {}
        
        # Cache statistics
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'updates': 0
        }
        
        logger.info("Threat intelligence database initialized")
    
    async def initialize_redis(self):
        """Initialize Redis connection"""



        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis initialized for threat intelligence")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def store_indicator(self, indicator: ThreatIndicator):
        """
        Store threat indicator in database
        
        Args:
            indicator: Threat indicator to store
        """



        try:
            # Store in memory cache
            self.indicators_cache[indicator.indicator_id] = indicator
            
            # Store in Redis for persistence
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                
                # Serialize indicator
                indicator_data = {
                    'indicator_id': indicator.indicator_id,
                    'indicator_type': indicator.indicator_type.value,
                    'indicator_value': indicator.indicator_value,
                    'threat_types': [t.value for t in indicator.threat_types],
                    'confidence': indicator.confidence.value,
                    'source': indicator.source.value,
                    'first_seen': indicator.first_seen.isoformat(),
                    'last_seen': indicator.last_seen.isoformat(),
                    'description': indicator.description,
                    'tags': list(indicator.tags),
                    'context': indicator.context,
                    'ttl': indicator.ttl,
                    'is_active': indicator.is_active
                }
                
                # Store with TTL
                await redis_client.setex(
                    f"indicator:{indicator.indicator_id}",
                    indicator.ttl,
                    json.dumps(indicator_data)
                )
                
                # Create indexes for fast lookups
                await redis_client.sadd(
                    f"indicators_by_type:{indicator.indicator_type.value}",
                    indicator.indicator_id
                )
                
                await redis_client.sadd(
                    f"indicators_by_value:{indicator.indicator_value}",
                    indicator.indicator_id
                )
                
                await redis_client.close()
            
            self.cache_stats['updates'] += 1
            logger.debug(f"Stored indicator: {indicator.indicator_id}")
            
        except Exception as e:
            logger.error(f"Failed to store indicator: {e}")
    
    async def lookup_indicator(self, indicator_value: str) -> Optional[ThreatIndicator]:
        """
        Lookup threat indicator by value
        
        Args:
            indicator_value: Indicator value to lookup
            
        Returns:
            Threat indicator if found
        """



        try:
            # Check memory cache first
            for indicator in self.indicators_cache.values():
                if indicator.indicator_value == indicator_value and indicator.is_active:
                    self.cache_stats['hits'] += 1
                    return indicator
            
            # Check Redis
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                
                # Get indicator IDs for this value
                indicator_ids = await redis_client.smembers(f"indicators_by_value:{indicator_value}")
                
                for indicator_id in indicator_ids:
                    indicator_data = await redis_client.get(f"indicator:{indicator_id.decode()}")
                    
                    if indicator_data:
                        data = json.loads(indicator_data)
                        
                        # Reconstruct indicator object
                        indicator = ThreatIndicator(
                            indicator_id=data['indicator_id'],
                            indicator_type=IndicatorType(data['indicator_type']),
                            indicator_value=data['indicator_value'],
                            threat_types=[ThreatType(t) for t in data['threat_types']],
                            confidence=ConfidenceLevel(data['confidence']),
                            source=ThreatIntelligenceSource(data['source']),
                            first_seen=datetime.fromisoformat(data['first_seen']),
                            last_seen=datetime.fromisoformat(data['last_seen']),
                            description=data['description'],
                            tags=set(data['tags']),
                            context=data['context'],
                            ttl=data['ttl'],
                            is_active=data['is_active']
                        )
                        
                        # Add to memory cache
                        self.indicators_cache[indicator.indicator_id] = indicator
                        
                        await redis_client.close()
                        self.cache_stats['hits'] += 1
                        return indicator
                
                await redis_client.close()
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Failed to lookup indicator: {e}")
            return None
    
    async def get_indicators_by_type(self, indicator_type: IndicatorType) -> List[ThreatIndicator]:
        """Get all indicators of specific type"""



        try:
            indicators = []
            
            # Get from memory cache
            for indicator in self.indicators_cache.values():
                if indicator.indicator_type == indicator_type and indicator.is_active:
                    indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get indicators by type: {e}")
            return []
    
    async def update_indicator_last_seen(self, indicator_id: str):
        """Update indicator last seen timestamp"""



        try:
            if indicator_id in self.indicators_cache:
                self.indicators_cache[indicator_id].last_seen = datetime.utcnow()
                
                # Update in Redis
                if self.redis_pool:
                    redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                    
                    indicator_data = await redis_client.get(f"indicator:{indicator_id}")
                    if indicator_data:
                        data = json.loads(indicator_data)
                        data['last_seen'] = datetime.utcnow().isoformat()
                        
                        await redis_client.setex(
                            f"indicator:{indicator_id}",
                            data['ttl'],
                            json.dumps(data)
                        )
                    
                    await redis_client.close()
                
                logger.debug(f"Updated last seen for indicator: {indicator_id}")
                
        except Exception as e:
            logger.error(f"Failed to update indicator last seen: {e}")
    
    async def cleanup_expired_indicators(self):
        """Cleanup expired indicators from cache"""



        try:
            current_time = datetime.utcnow()
            expired_ids = []
            
            for indicator_id, indicator in self.indicators_cache.items():
                # Check if indicator has expired
                if (current_time - indicator.last_seen).total_seconds() > indicator.ttl:
                    expired_ids.append(indicator_id)
            
            # Remove expired indicators
            for indicator_id in expired_ids:
                del self.indicators_cache[indicator_id]
            
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired indicators")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired indicators: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_indicators': len(self.indicators_cache),
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'cache_hit_rate': round(hit_rate, 2),
            'total_updates': self.cache_stats['updates']
        }


class ThreatIntelligenceCollector:
    """
    Automated threat intelligence collection from multiple sources
    """
    
    def __init__(
        self,
        database: ThreatIntelligenceDatabase,
        virustotal_api_key: str = None,
        otx_api_key: str = None
    ):
        self.database = database
        self.virustotal_api_key = virustotal_api_key
        self.otx_api_key = otx_api_key
        
        # Collection status
        self.collection_active = False
        self.last_collection_time = None
        
        # Collection statistics
        self.collection_stats = defaultdict(int)
        
        logger.info("Threat intelligence collector initialized")
    
    async def start_collection(self, collection_interval: int = 3600):
        """
        Start automated threat intelligence collection
        
        Args:
            collection_interval: Collection interval in seconds
        """



        try:
            self.collection_active = True
            
            while self.collection_active:
                try:
                    logger.info("Starting threat intelligence collection cycle")
                    
                    # Collect from VirusTotal
                    if self.virustotal_api_key:
                        await self._collect_from_virustotal()
                    
                    # Collect from OTX
                    if self.otx_api_key:
                        await self._collect_from_otx()
                    
                    # Collect from OSINT sources
                    await self._collect_from_osint()
                    
                    self.last_collection_time = datetime.utcnow()
                    logger.info("Threat intelligence collection cycle completed")
                    
                    # Wait for next collection cycle
                    await asyncio.sleep(collection_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in collection cycle: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
            
        except Exception as e:
            logger.error(f"Failed to start threat intelligence collection: {e}")
        finally:
            self.collection_active = False
    
    async def stop_collection(self):
        """Stop threat intelligence collection"""
        self.collection_active = False
        logger.info("Threat intelligence collection stopped")
    
    async def _collect_from_virustotal(self):
        """Collect threat intelligence from VirusTotal"""



        try:
            async with VirusTotalClient(self.virustotal_api_key) as vt_client:
                # Get recent malicious IPs (this is a simplified example)
                # In production, you would have specific IoCs to check
                suspicious_ips = [
                    "192.168.1.100",  # Example IPs
                    "10.0.0.1"
                ]
                
                for ip in suspicious_ips:
                    try:
                        vt_data = await vt_client.lookup_ip(ip)
                        
                        if vt_data and vt_data.get('response_code') == 1:
                            # Create threat indicator from VT data
                            indicator = await self._create_indicator_from_vt_ip(ip, vt_data)
                            
                            if indicator:
                                await self.database.store_indicator(indicator)
                                self.collection_stats['virustotal_indicators'] += 1
                        
                        # Rate limiting
                        await asyncio.sleep(15)  # VT free API limit
                        
                    except Exception as e:
                        logger.warning(f"Failed to process VT IP {ip}: {e}")
                
                logger.info(f"VirusTotal collection completed: {self.collection_stats['virustotal_indicators']} indicators")
                
        except Exception as e:
            logger.error(f"VirusTotal collection failed: {e}")
    
    async def _create_indicator_from_vt_ip(self, ip: str, vt_data: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Create threat indicator from VirusTotal IP data"""



        try:
            detected_urls = vt_data.get('detected_urls', [])
            detected_samples = vt_data.get('detected_communicating_samples', [])
            
            # Determine threat types
            threat_types = []
            if detected_urls:
                threat_types.append(ThreatType.MALWARE)
            if detected_samples:
                threat_types.append(ThreatType.C2_SERVER)
            
            if not threat_types:
                return None
            
            # Calculate confidence based on detections
            total_detections = len(detected_urls) + len(detected_samples)
            if total_detections > 10:
                confidence = ConfidenceLevel.HIGH
            elif total_detections > 5:
                confidence = ConfidenceLevel.MEDIUM
            else:
                confidence = ConfidenceLevel.LOW
            
            indicator_id = f"vt_ip_{hashlib.md5(ip.encode()).hexdigest()}"
            
            indicator = ThreatIndicator(
                indicator_id=indicator_id,
                indicator_type=IndicatorType.IP_ADDRESS,
                indicator_value=ip,
                threat_types=threat_types,
                confidence=confidence,
                source=ThreatIntelligenceSource.VIRUSTOTAL,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                description=f"Malicious IP detected by VirusTotal with {total_detections} detections",
                tags={'virustotal', 'automated'},
                context={
                    'detected_urls_count': len(detected_urls),
                    'detected_samples_count': len(detected_samples),
                    'vt_permalink': vt_data.get('permalink', '')
                }
            )
            
            return indicator
            
        except Exception as e:
            logger.error(f"Failed to create VT indicator: {e}")
            return None
    
    async def _collect_from_otx(self):
        """Collect threat intelligence from AlienVault OTX"""



        try:
            async with AlienVaultOTXClient(self.otx_api_key) as otx_client:
                # Get recent pulses
                recent_pulses = await otx_client.get_pulses(
                    modified_since=datetime.utcnow() - timedelta(hours=24)
                )
                
                for pulse in recent_pulses:
                    try:
                        indicators = pulse.get('indicators', [])
                        
                        for indicator_data in indicators:
                            indicator = await self._create_indicator_from_otx_pulse(pulse, indicator_data)
                            
                            if indicator:
                                await self.database.store_indicator(indicator)
                                self.collection_stats['otx_indicators'] += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to process OTX pulse: {e}")
                
                logger.info(f"OTX collection completed: {self.collection_stats['otx_indicators']} indicators")
                
        except Exception as e:
            logger.error(f"OTX collection failed: {e}")
    
    async def _create_indicator_from_otx_pulse(
        self,
        pulse: Dict[str, Any],
        indicator_data: Dict[str, Any]
    ) -> Optional[ThreatIndicator]:
        """Create threat indicator from OTX pulse data"""



        try:
            indicator_type_map = {
                'IPv4': IndicatorType.IP_ADDRESS,
                'domain': IndicatorType.DOMAIN,
                'URL': IndicatorType.URL,
                'FileHash-MD5': IndicatorType.FILE_HASH,
                'FileHash-SHA1': IndicatorType.FILE_HASH,
                'FileHash-SHA256': IndicatorType.FILE_HASH
            }
            
            otx_type = indicator_data.get('type')
            indicator_type = indicator_type_map.get(otx_type)
            
            if not indicator_type:
                return None
            
            # Map pulse tags to threat types
            pulse_tags = pulse.get('tags', [])
            threat_types = []
            
            if any(tag in ['malware', 'trojan', 'virus'] for tag in pulse_tags):
                threat_types.append(ThreatType.MALWARE)
            if any(tag in ['phishing', 'scam'] for tag in pulse_tags):
                threat_types.append(ThreatType.PHISHING)
            if any(tag in ['apt', 'campaign'] for tag in pulse_tags):
                threat_types.append(ThreatType.APT)
            
            if not threat_types:
                threat_types = [ThreatType.SUSPICIOUS]
            
            indicator_id = f"otx_{hashlib.md5(f"{pulse['id']}_{indicator_data['indicator']}".encode()).hexdigest()}"
            
            indicator = ThreatIndicator(
                indicator_id=indicator_id,
                indicator_type=indicator_type,
                indicator_value=indicator_data['indicator'],
                threat_types=threat_types,
                confidence=ConfidenceLevel.MEDIUM,  # OTX generally has good quality
                source=ThreatIntelligenceSource.ALIENVAULT_OTX,
                first_seen=datetime.fromisoformat(pulse['created'].replace('Z', '+00:00')),
                last_seen=datetime.fromisoformat(pulse['modified'].replace('Z', '+00:00')),
                description=pulse.get('description', f"Indicator from OTX pulse: {pulse['name']}"),
                tags=set(pulse_tags + ['otx', 'automated']),
                context={
                    'pulse_id': pulse['id'],
                    'pulse_name': pulse['name'],
                    'author_name': pulse.get('author_name', ''),
                    'industries': pulse.get('industries', []),
                    'malware_families': pulse.get('malware_families', [])
                }
            )
            
            return indicator
            
        except Exception as e:
            logger.error(f"Failed to create OTX indicator: {e}")
            return None
    
    async def _collect_from_osint(self):
        """Collect threat intelligence from OSINT sources"""



        try:
            # Collect from public blacklists and threat feeds
            # This is a simplified example - in production you would have more sources
            
            osint_sources = [
                {
                    'name': 'abuse.ch_feodo',
                    'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist.txt',
                    'type': 'ip_list'
                },
                {
                    'name': 'malwaredomainlist',
                    'url': 'http://www.malwaredomainlist.com/hostslist/hosts.txt',
                    'type': 'domain_list'
                }
            ]
            
            async with aiohttp.ClientSession() as session:
                for source in osint_sources:
                    try:
                        await self._collect_from_osint_source(session, source)
                    except Exception as e:
                        logger.warning(f"Failed to collect from {source['name']}: {e}")
            
            logger.info(f"OSINT collection completed: {self.collection_stats['osint_indicators']} indicators")
            
        except Exception as e:
            logger.error(f"OSINT collection failed: {e}")
    
    async def _collect_from_osint_source(
        self,
        session: aiohttp.ClientSession,
        source: Dict[str, str]
    ):
        """Collect from individual OSINT source"""



        try:
            async with session.get(source['url'], timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    if source['type'] == 'ip_list':
                        await self._process_ip_list(content, source['name'])
                    elif source['type'] == 'domain_list':
                        await self._process_domain_list(content, source['name'])
                        
        except Exception as e:
            logger.error(f"Failed to collect from OSINT source {source['name']}: {e}")
    
    async def _process_ip_list(self, content: str, source_name: str):
        """Process IP list from OSINT source"""



        try:
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Validate IP address
                try:
                    ipaddress.ip_address(line)
                    
                    # Create indicator
                    indicator_id = f"osint_{source_name}_{hashlib.md5(line.encode()).hexdigest()}"
                    
                    indicator = ThreatIndicator(
                        indicator_id=indicator_id,
                        indicator_type=IndicatorType.IP_ADDRESS,
                        indicator_value=line,
                        threat_types=[ThreatType.MALWARE],
                        confidence=ConfidenceLevel.MEDIUM,
                        source=ThreatIntelligenceSource.OSINT,
                        first_seen=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        description=f"Malicious IP from {source_name}",
                        tags={source_name, 'osint', 'automated'},
                        context={'osint_source': source_name}
                    )
                    
                    await self.database.store_indicator(indicator)
                    self.collection_stats['osint_indicators'] += 1
                    
                except ValueError:
                    continue  # Invalid IP address
                    
        except Exception as e:
            logger.error(f"Failed to process IP list from {source_name}: {e}")
    
    async def _process_domain_list(self, content: str, source_name: str):
        """Process domain list from OSINT source"""



        try:
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Extract domain from hosts file format
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        domain = parts[1].strip()
                    else:
                        continue
                else:
                    domain = line
                
                # Basic domain validation
                if '.' not in domain or len(domain) < 4:
                    continue
                
                # Create indicator
                indicator_id = f"osint_{source_name}_{hashlib.md5(domain.encode()).hexdigest()}"
                
                indicator = ThreatIndicator(
                    indicator_id=indicator_id,
                    indicator_type=IndicatorType.DOMAIN,
                    indicator_value=domain,
                    threat_types=[ThreatType.MALWARE],
                    confidence=ConfidenceLevel.MEDIUM,
                    source=ThreatIntelligenceSource.OSINT,
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    description=f"Malicious domain from {source_name}",
                    tags={source_name, 'osint', 'automated'},
                    context={'osint_source': source_name}
                )
                
                await self.database.store_indicator(indicator)
                self.collection_stats['osint_indicators'] += 1
                
        except Exception as e:
            logger.error(f"Failed to process domain list from {source_name}: {e}")
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence collection statistics"""



        return {
            'collection_active': self.collection_active,
            'last_collection_time': self.last_collection_time.isoformat() if self.last_collection_time else None,
            'indicators_collected': dict(self.collection_stats),
            'total_indicators_collected': sum(self.collection_stats.values())
        }


class ThreatIntelligenceEngine:
    """
    Main threat intelligence engine combining collection, analysis, and lookup
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        virustotal_api_key: str = None,
        otx_api_key: str = None
    ):
        self.database = ThreatIntelligenceDatabase(redis_url)
        self.collector = ThreatIntelligenceCollector(
            database=self.database,
            virustotal_api_key=virustotal_api_key,
            otx_api_key=otx_api_key
        )
        
        # Engine status
        self.engine_active = False
        self._collection_task = None
        self._cleanup_task = None
        
        logger.info("Threat intelligence engine initialized")
    
    async def start_engine(self, collection_interval: int = 3600):
        """
        Start threat intelligence engine
        
        Args:
            collection_interval: Collection interval in seconds
        """



        try:
            await self.database.initialize_redis()
            
            self.engine_active = True
            
            # Start collection task
            self._collection_task = asyncio.create_task(
                self.collector.start_collection(collection_interval)
            )
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Threat intelligence engine started")
            
        except Exception as e:
            logger.error(f"Failed to start threat intelligence engine: {e}")
            raise
    
    async def stop_engine(self):
        """Stop threat intelligence engine"""



        try:
            self.engine_active = False
            
            # Stop collector
            await self.collector.stop_collection()
            
            # Cancel tasks
            if self._collection_task:
                self._collection_task.cancel()
            
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            logger.info("Threat intelligence engine stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop threat intelligence engine: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.engine_active:
            try:
                # Cleanup expired indicators every hour
                await asyncio.sleep(3600)
                await self.database.cleanup_expired_indicators()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def lookup_threat_intelligence(
        self,
        indicator_value: str,
        update_last_seen: bool = True
    ) -> Optional[ThreatIndicator]:
        """
        Lookup threat intelligence for indicator
        
        Args:
            indicator_value: Indicator value to lookup
            update_last_seen: Whether to update last seen timestamp
            
        Returns:
            Threat indicator if found
        """



        try:
            indicator = await self.database.lookup_indicator(indicator_value)
            
            if indicator and update_last_seen:
                await self.database.update_indicator_last_seen(indicator.indicator_id)
            
            return indicator
            
        except Exception as e:
            logger.error(f"Failed to lookup threat intelligence: {e}")
            return None
    
    async def enrich_with_threat_intelligence(
        self,
        indicators: List[str]
    ) -> Dict[str, Optional[ThreatIndicator]]:
        """
        Enrich multiple indicators with threat intelligence
        
        Args:
            indicators: List of indicator values to enrich
            
        Returns:
            Dictionary mapping indicators to threat intelligence
        """



        try:
            enriched_data = {}
            
            # Lookup each indicator
            for indicator_value in indicators:
                threat_intel = await self.lookup_threat_intelligence(indicator_value)
                enriched_data[indicator_value] = threat_intel
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Failed to enrich with threat intelligence: {e}")
            return {}
    
    async def add_custom_indicator(
        self,
        indicator_value: str,
        indicator_type: IndicatorType,
        threat_types: List[ThreatType],
        confidence: ConfidenceLevel,
        description: str,
        tags: Set[str] = None,
        context: Dict[str, Any] = None
    ) -> ThreatIndicator:
        """
        Add custom threat indicator
        
        Args:
            indicator_value: Indicator value
            indicator_type: Type of indicator
            threat_types: List of threat types
            confidence: Confidence level
            description: Description
            tags: Optional tags
            context: Optional context data
            
        Returns:
            Created threat indicator
        """



        try:
            indicator_id = f"custom_{hashlib.md5(f"{indicator_value}_{int(time.time())}".encode()).hexdigest()}"
            
            indicator = ThreatIndicator(
                indicator_id=indicator_id,
                indicator_type=indicator_type,
                indicator_value=indicator_value,
                threat_types=threat_types,
                confidence=confidence,
                source=ThreatIntelligenceSource.INTERNAL,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                description=description,
                tags=tags or {'custom', 'internal'},
                context=context or {}
            )
            
            await self.database.store_indicator(indicator)
            
            logger.info(f"Custom indicator added: {indicator_id}")
            return indicator
            
        except Exception as e:
            logger.error(f"Failed to add custom indicator: {e}")
            raise
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get threat intelligence engine status"""



        try:
            cache_stats = self.database.get_cache_statistics()
            collection_stats = self.collector.get_collection_statistics()
            
            return {
                'engine_active': self.engine_active,
                'database_status': cache_stats,
                'collection_status': collection_stats,
                'total_indicators': cache_stats['total_indicators']
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine status: {e}")
            return {"error": str(e)}


# Export main classes for module usage
__all__ = [
    'ThreatIntelligenceEngine',
    'ThreatIntelligenceDatabase',
    'ThreatIntelligenceCollector',
    'ThreatIndicator',
    'ThreatCampaign',
    'ThreatActor',
    'IndicatorType',
    'ThreatType',
    'ConfidenceLevel',
    'ThreatIntelligenceSource'
]
