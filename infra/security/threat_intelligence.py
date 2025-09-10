# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Threat Intelligence

Enterprise threat intelligence system for proactive security management.
Integrates with threat feeds, analyzes indicators, and provides actionable intelligence.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import ipaddress
from urllib.parse import urlparse
import requests
import aiohttp


class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    APT = "apt"
    DDOS = "ddos"
    MALICIOUS_IP = "malicious_ip"
    MALICIOUS_DOMAIN = "malicious_domain"
    MALICIOUS_URL = "malicious_url"
    SUSPICIOUS_EMAIL = "suspicious_email"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    INSIDER_THREAT = "insider_threat"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IndicatorType(Enum):
    """Types of threat indicators"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    USER_AGENT = "user_agent"
    SSL_CERT_HASH = "ssl_cert_hash"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    YARA_RULE = "yara_rule"


class Confidence(Enum):
    """Confidence levels for threat intelligence"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class ThreatIndicator:
    """Threat indicator of compromise (IoC)"""
    id: str
    type: IndicatorType
    value: str
    threat_types: List[ThreatType]
    severity: ThreatSeverity
    confidence: Confidence
    source: str
    description: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[int] = None  # Time to live in seconds
    false_positive: bool = False


@dataclass
class ThreatReport:
    """Threat intelligence report"""
    id: str
    title: str
    description: str
    threat_types: List[ThreatType]
    severity: ThreatSeverity
    indicators: List[ThreatIndicator]
    attribution: Optional[str] = None
    campaign: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "internal"
    references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ThreatMatch:
    """Threat intelligence match result"""
    indicator: ThreatIndicator
    matched_value: str
    match_type: str
    confidence_score: float
    context: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


class ThreatIntelligence:
    """
    Enterprise threat intelligence system
    
    Provides comprehensive threat intelligence capabilities including:
    - Threat feed integration
    - Indicator of compromise (IoC) management
    - Threat analysis and correlation
    - Real-time threat detection
    - Threat hunting support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.reports: Dict[str, ThreatReport] = {}
        self.feed_sources = self._setup_threat_feeds()
        self.whitelist: Set[str] = set(self.config.get('whitelist', []))
        self.api_keys = self.config.get('api_keys', {})
        
        # Cache for performance
        self.ip_cache: Dict[str, ThreatMatch] = {}
        self.domain_cache: Dict[str, ThreatMatch] = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
    
    def _setup_threat_feeds(self) -> Dict[str, Dict[str, Any]]:
        """Setup threat intelligence feed sources"""
        
        return {
            'abuse_ch': {
                'name': 'Abuse.ch',
                'url': 'https://urlhaus-api.abuse.ch/v1/payloads/recent/',
                'type': 'malware',
                'format': 'json',
                'enabled': True,
                'update_interval': 3600  # 1 hour
            },
            'malware_bazaar': {
                'name': 'Malware Bazaar',
                'url': 'https://mb-api.abuse.ch/api/v1/',
                'type': 'malware',
                'format': 'json',
                'enabled': True,
                'update_interval': 3600
            },
            'feodo_tracker': {
                'name': 'Feodo Tracker',
                'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
                'type': 'botnet',
                'format': 'csv',
                'enabled': True,
                'update_interval': 1800  # 30 minutes
            },
            'virustotal': {
                'name': 'VirusTotal',
                'url': 'https://www.virustotal.com/vtapi/v2/',
                'type': 'malware',
                'format': 'json',
                'enabled': bool(self.api_keys.get('virustotal')),
                'update_interval': 7200,  # 2 hours
                'api_key': self.api_keys.get('virustotal')
            },
            'misp': {
                'name': 'MISP',
                'url': self.config.get('misp_url'),
                'type': 'general',
                'format': 'json',
                'enabled': bool(self.config.get('misp_url')),
                'update_interval': 1800,
                'api_key': self.api_keys.get('misp')
            },
            'otx': {
                'name': 'AlienVault OTX',
                'url': 'https://otx.alienvault.com/api/v1/',
                'type': 'general',
                'format': 'json',
                'enabled': bool(self.api_keys.get('otx')),
                'update_interval': 3600,
                'api_key': self.api_keys.get('otx')
            }
        }
    
    async def start_intelligence_feeds(self):
        """Start automated threat intelligence feed updates"""
        
        self.logger.info("Starting threat intelligence feed updates")
        
        # Create background tasks for each enabled feed
        tasks = []
        for feed_name, feed_config in self.feed_sources.items():
            if feed_config['enabled']:
                task = asyncio.create_task(
                    self._update_feed_loop(feed_name, feed_config)
                )
                tasks.append(task)
        
        # Start cache cleanup task
        cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        tasks.append(cleanup_task)
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _update_feed_loop(self, feed_name: str, feed_config: Dict[str, Any]):
        """Update loop for a specific threat feed"""
        
        while True:
            try:
                self.logger.info(f"Updating threat feed: {feed_name}")
                await self._update_threat_feed(feed_name, feed_config)
                
                # Wait for next update
                await asyncio.sleep(feed_config['update_interval'])
                
            except Exception as e:
                self.logger.error(f"Error updating feed {feed_name}: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _update_threat_feed(self, feed_name: str, feed_config: Dict[str, Any]):
        """Update indicators from a specific threat feed"""
        
        try:
            if feed_name == 'abuse_ch':
                await self._update_abuse_ch_feed(feed_config)
            elif feed_name == 'feodo_tracker':
                await self._update_feodo_tracker_feed(feed_config)
            elif feed_name == 'virustotal':
                await self._update_virustotal_feed(feed_config)
            elif feed_name == 'misp':
                await self._update_misp_feed(feed_config)
            elif feed_name == 'otx':
                await self._update_otx_feed(feed_config)
            else:
                self.logger.warning(f"Unknown feed type: {feed_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to update feed {feed_name}: {str(e)}")
    
    async def _update_abuse_ch_feed(self, feed_config: Dict[str, Any]):
        """Update indicators from Abuse.ch URLhaus"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_config['url']) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for payload in data.get('payloads', []):
                        # Create indicator for malware URL
                        indicator = ThreatIndicator(
                            id=f"abuse_ch_{hashlib.sha256(payload['url'].encode()).hexdigest()[:12]}",
                            type=IndicatorType.URL,
                            value=payload['url'],
                            threat_types=[ThreatType.MALWARE],
                            severity=ThreatSeverity.HIGH,
                            confidence=Confidence.HIGH,
                            source='abuse.ch',
                            description=f"Malware payload URL - {payload.get('signature', 'Unknown')}",
                            first_seen=datetime.fromisoformat(payload['firstseen'].replace('Z', '+00:00')),
                            last_seen=datetime.fromisoformat(payload['lastseen'].replace('Z', '+00:00')),
                            tags=['malware', 'payload'],
                            context={
                                'signature': payload.get('signature'),
                                'file_type': payload.get('file_type'),
                                'response_size': payload.get('response_size')
                            }
                        )
                        
                        self.indicators[indicator.id] = indicator
                    
                    self.logger.info(f"Updated {len(data.get('payloads', []))} indicators from Abuse.ch")
    
    async def _update_feodo_tracker_feed(self, feed_config: Dict[str, Any]):
        """Update indicators from Feodo Tracker"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_config['url']) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.strip().split('\n')
                    
                    count = 0
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse CSV format: IP,port,status,hostname,as_number,as_name,country
                            parts = line.split(',')
                            if len(parts) >= 3:
                                ip = parts[0].strip()
                                port = parts[1].strip()
                                
                                # Validate IP address
                                try:
                                    ipaddress.ip_address(ip)
                                    
                                    indicator = ThreatIndicator(
                                        id=f"feodo_{hashlib.sha256(f'{ip}:{port}'.encode()).hexdigest()[:12]}",
                                        type=IndicatorType.IP_ADDRESS,
                                        value=ip,
                                        threat_types=[ThreatType.BOTNET],
                                        severity=ThreatSeverity.HIGH,
                                        confidence=Confidence.HIGH,
                                        source='feodo_tracker',
                                        description=f"Botnet C&C server on port {port}",
                                        first_seen=datetime.utcnow(),
                                        last_seen=datetime.utcnow(),
                                        tags=['botnet', 'c2'],
                                        context={'port': port}
                                    )
                                    
                                    self.indicators[indicator.id] = indicator
                                    count += 1
                                
                                except ValueError:
                                    continue
                    
                    self.logger.info(f"Updated {count} indicators from Feodo Tracker")
    
    async def _update_virustotal_feed(self, feed_config: Dict[str, Any]):
        """Update indicators from VirusTotal"""
        
        if not feed_config.get('api_key'):
            return
        
        # This would implement VirusTotal API integration
        # For now, we'll create a placeholder
        self.logger.info("VirusTotal feed integration placeholder")
    
    async def _update_misp_feed(self, feed_config: Dict[str, Any]):
        """Update indicators from MISP"""
        
        if not feed_config.get('url') or not feed_config.get('api_key'):
            return
        
        # This would implement MISP API integration
        # For now, we'll create a placeholder
        self.logger.info("MISP feed integration placeholder")
    
    async def _update_otx_feed(self, feed_config: Dict[str, Any]):
        """Update indicators from AlienVault OTX"""
        
        if not feed_config.get('api_key'):
            return
        
        # This would implement OTX API integration
        # For now, we'll create a placeholder
        self.logger.info("OTX feed integration placeholder")
    
    async def _cache_cleanup_loop(self):
        """Clean up expired cache entries"""
        
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Clean IP cache
                expired_ips = []
                for ip, match in self.ip_cache.items():
                    if (current_time - match.detected_at).seconds > self.cache_ttl:
                        expired_ips.append(ip)
                
                for ip in expired_ips:
                    del self.ip_cache[ip]
                
                # Clean domain cache
                expired_domains = []
                for domain, match in self.domain_cache.items():
                    if (current_time - match.detected_at).seconds > self.cache_ttl:
                        expired_domains.append(domain)
                
                for domain in expired_domains:
                    del self.domain_cache[domain]
                
                if expired_ips or expired_domains:
                    self.logger.debug(f"Cleaned {len(expired_ips)} IP and {len(expired_domains)} domain cache entries")
                
                # Sleep for cache cleanup interval
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in cache cleanup: {str(e)}")
                await asyncio.sleep(60)
    
    async def check_indicator(self, value: str, indicator_type: IndicatorType) -> Optional[ThreatMatch]:
        """
        Check if a value matches any threat indicators
        
        Args:
            value: Value to check (IP, domain, URL, etc.)
            indicator_type: Type of indicator
            
        Returns:
            ThreatMatch if found, None otherwise
        """
        # Check whitelist first
        if value in self.whitelist:
            return None
        
        # Check cache
        cache_key = f"{indicator_type.value}:{value}"
        if indicator_type == IndicatorType.IP_ADDRESS and value in self.ip_cache:
            return self.ip_cache[value]
        elif indicator_type == IndicatorType.DOMAIN and value in self.domain_cache:
            return self.domain_cache[value]
        
        # Check indicators
        for indicator in self.indicators.values():
            if indicator.type == indicator_type:
                match = await self._match_indicator(value, indicator)
                if match:
                    # Cache the result
                    if indicator_type == IndicatorType.IP_ADDRESS:
                        self.ip_cache[value] = match
                    elif indicator_type == IndicatorType.DOMAIN:
                        self.domain_cache[value] = match
                    
                    return match
        
        return None
    
    async def _match_indicator(self, value: str, indicator: ThreatIndicator) -> Optional[ThreatMatch]:
        """Check if a value matches a specific indicator"""
        
        # Exact match
        if value == indicator.value:
            return ThreatMatch(
                indicator=indicator,
                matched_value=value,
                match_type="exact",
                confidence_score=1.0
            )
        
        # Fuzzy matching for domains and URLs
        if indicator.type in [IndicatorType.DOMAIN, IndicatorType.URL]:
            # Subdomain matching
            if indicator.type == IndicatorType.DOMAIN:
                if value.endswith(f".{indicator.value}"):
                    return ThreatMatch(
                        indicator=indicator,
                        matched_value=value,
                        match_type="subdomain",
                        confidence_score=0.8
                    )
            
            # URL path matching
            elif indicator.type == IndicatorType.URL:
                if indicator.value in value:
                    return ThreatMatch(
                        indicator=indicator,
                        matched_value=value,
                        match_type="partial_url",
                        confidence_score=0.7
                    )
        
        # IP range matching
        elif indicator.type == IndicatorType.IP_ADDRESS:
            try:
                # Check if indicator is a CIDR range
                if '/' in indicator.value:
                    network = ipaddress.ip_network(indicator.value, strict=False)
                    if ipaddress.ip_address(value) in network:
                        return ThreatMatch(
                            indicator=indicator,
                            matched_value=value,
                            match_type="ip_range",
                            confidence_score=0.9
                        )
            except ValueError:
                pass
        
        return None
    
    async def bulk_check_indicators(self, values: List[str], indicator_type: IndicatorType) -> Dict[str, ThreatMatch]:
        """
        Check multiple values against threat indicators
        
        Args:
            values: List of values to check
            indicator_type: Type of indicators
            
        Returns:
            Dictionary of matches {value: ThreatMatch}
        """
        matches = {}
        
        # Use asyncio.gather for concurrent checking
        tasks = [self.check_indicator(value, indicator_type) for value in values]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for value, result in zip(values, results):
            if isinstance(result, ThreatMatch):
                matches[value] = result
        
        return matches
    
    def add_custom_indicator(self, indicator: ThreatIndicator):
        """Add a custom threat indicator"""
        
        # Validate indicator
        if not indicator.value or not indicator.type:
            raise ValueError("Indicator must have value and type")
        
        # Check for duplicates
        existing = self._find_existing_indicator(indicator.value, indicator.type)
        if existing:
            self.logger.warning(f"Indicator {indicator.value} already exists, updating...")
            indicator.id = existing.id
        
        self.indicators[indicator.id] = indicator
        self.logger.info(f"Added custom indicator: {indicator.value} ({indicator.type.value})")
    
    def remove_indicator(self, indicator_id: str):
        """Remove a threat indicator"""
        
        if indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            del self.indicators[indicator_id]
            self.logger.info(f"Removed indicator: {indicator.value} ({indicator.type.value})")
        else:
            raise ValueError(f"Indicator {indicator_id} not found")
    
    def mark_false_positive(self, indicator_id: str):
        """Mark an indicator as false positive"""
        
        if indicator_id in self.indicators:
            self.indicators[indicator_id].false_positive = True
            self.logger.info(f"Marked indicator {indicator_id} as false positive")
        else:
            raise ValueError(f"Indicator {indicator_id} not found")
    
    def _find_existing_indicator(self, value: str, indicator_type: IndicatorType) -> Optional[ThreatIndicator]:
        """Find existing indicator by value and type"""
        
        for indicator in self.indicators.values():
            if indicator.value == value and indicator.type == indicator_type:
                return indicator
        
        return None
    
    def create_threat_report(
        self,
        title: str,
        description: str,
        threat_types: List[ThreatType],
        severity: ThreatSeverity,
        indicators: List[ThreatIndicator],
        attribution: Optional[str] = None,
        campaign: Optional[str] = None,
        references: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> ThreatReport:
        """Create a new threat intelligence report"""
        
        report = ThreatReport(
            id=f"report_{hashlib.sha256(f'{title}_{datetime.utcnow()}'.encode()).hexdigest()[:12]}",
            title=title,
            description=description,
            threat_types=threat_types,
            severity=severity,
            indicators=indicators,
            attribution=attribution,
            campaign=campaign,
            references=references or [],
            tags=tags or []
        )
        
        self.reports[report.id] = report
        
        # Add indicators to the main indicator store
        for indicator in indicators:
            self.indicators[indicator.id] = indicator
        
        self.logger.info(f"Created threat report: {title} with {len(indicators)} indicators")
        
        return report
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get threat intelligence summary statistics"""
        
        summary = {
            'total_indicators': len(self.indicators),
            'total_reports': len(self.reports),
            'indicator_types': {},
            'threat_types': {},
            'severity_levels': {},
            'sources': {},
            'cache_stats': {
                'ip_cache_size': len(self.ip_cache),
                'domain_cache_size': len(self.domain_cache)
            }
        }
        
        # Count by indicator type
        for indicator_type in IndicatorType:
            summary['indicator_types'][indicator_type.value] = len([
                i for i in self.indicators.values() if i.type == indicator_type
            ])
        
        # Count by threat type
        for threat_type in ThreatType:
            count = 0
            for indicator in self.indicators.values():
                if threat_type in indicator.threat_types:
                    count += 1
            summary['threat_types'][threat_type.value] = count
        
        # Count by severity
        for severity in ThreatSeverity:
            summary['severity_levels'][severity.value] = len([
                i for i in self.indicators.values() if i.severity == severity
            ])
        
        # Count by source
        sources = set(i.source for i in self.indicators.values())
        for source in sources:
            summary['sources'][source] = len([
                i for i in self.indicators.values() if i.source == source
            ])
        
        return summary
    
    async def hunt_threats(
        self,
        hunt_query: Dict[str, Any],
        time_range: Optional[Dict[str, datetime]] = None
    ) -> List[ThreatMatch]:
        """
        Perform threat hunting based on query criteria
        
        Args:
            hunt_query: Query criteria (threat_types, severity, etc.)
            time_range: Optional time range filter
            
        Returns:
            List of potential threat matches
        """
        matches = []
        
        # Filter indicators based on hunt query
        filtered_indicators = []
        
        for indicator in self.indicators.values():
            # Skip false positives
            if indicator.false_positive:
                continue
            
            # Check threat types
            if 'threat_types' in hunt_query:
                query_types = hunt_query['threat_types']
                if not any(t in indicator.threat_types for t in query_types):
                    continue
            
            # Check severity
            if 'severity' in hunt_query:
                if indicator.severity != hunt_query['severity']:
                    continue
            
            # Check confidence
            if 'min_confidence' in hunt_query:
                confidence_values = {'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
                if confidence_values.get(indicator.confidence.value, 0) < confidence_values.get(hunt_query['min_confidence'], 0):
                    continue
            
            # Check time range
            if time_range:
                start_time = time_range.get('start')
                end_time = time_range.get('end')
                
                if start_time and indicator.last_seen < start_time:
                    continue
                if end_time and indicator.first_seen > end_time:
                    continue
            
            filtered_indicators.append(indicator)
        
        # Create threat matches for filtered indicators
        for indicator in filtered_indicators:
            match = ThreatMatch(
                indicator=indicator,
                matched_value=indicator.value,
                match_type="hunt_query",
                confidence_score=1.0,
                context={'hunt_query': hunt_query}
            )
            matches.append(match)
        
        self.logger.info(f"Threat hunt returned {len(matches)} potential matches")
        
        return matches
    
    def export_indicators(
        self,
        format: str = "json",
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export threat indicators in specified format
        
        Args:
            format: Export format (json, csv, stix)
            filter_criteria: Optional filter criteria
            
        Returns:
            Exported data as string
        """
        # Filter indicators if criteria provided
        indicators_to_export = list(self.indicators.values())
        
        if filter_criteria:
            filtered = []
            for indicator in indicators_to_export:
                # Apply filters
                if 'threat_types' in filter_criteria:
                    if not any(t in indicator.threat_types for t in filter_criteria['threat_types']):
                        continue
                
                if 'severity' in filter_criteria:
                    if indicator.severity != filter_criteria['severity']:
                        continue
                
                if 'source' in filter_criteria:
                    if indicator.source != filter_criteria['source']:
                        continue
                
                filtered.append(indicator)
            
            indicators_to_export = filtered
        
        if format == "json":
            return self._export_json(indicators_to_export)
        elif format == "csv":
            return self._export_csv(indicators_to_export)
        elif format == "stix":
            return self._export_stix(indicators_to_export)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, indicators: List[ThreatIndicator]) -> str:
        """Export indicators as JSON"""
        
        data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_indicators': len(indicators),
            'indicators': [
                {
                    'id': i.id,
                    'type': i.type.value,
                    'value': i.value,
                    'threat_types': [t.value for t in i.threat_types],
                    'severity': i.severity.value,
                    'confidence': i.confidence.value,
                    'source': i.source,
                    'description': i.description,
                    'first_seen': i.first_seen.isoformat(),
                    'last_seen': i.last_seen.isoformat(),
                    'tags': i.tags,
                    'context': i.context,
                    'false_positive': i.false_positive
                }
                for i in indicators
            ]
        }
        
        return json.dumps(data, indent=2)
    
    def _export_csv(self, indicators: List[ThreatIndicator]) -> str:
        """Export indicators as CSV"""
        
        lines = ['id,type,value,threat_types,severity,confidence,source,description,first_seen,last_seen,false_positive']
        
        for indicator in indicators:
            threat_types = ';'.join(t.value for t in indicator.threat_types)
            line = f'"{indicator.id}","{indicator.type.value}","{indicator.value}","{threat_types}","{indicator.severity.value}","{indicator.confidence.value}","{indicator.source}","{indicator.description}","{indicator.first_seen.isoformat()}","{indicator.last_seen.isoformat()}",{indicator.false_positive}'
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _export_stix(self, indicators: List[ThreatIndicator]) -> str:
        """Export indicators as STIX format"""
        
        # This would implement proper STIX 2.0/2.1 format
        # For now, we'll create a simplified version
        
        stix_objects = []
        
        for indicator in indicators:
            stix_object = {
                'type': 'indicator',
                'id': f'indicator--{indicator.id}',
                'created': indicator.first_seen.isoformat(),
                'modified': indicator.last_seen.isoformat(),
                'pattern': f"[{indicator.type.value}:value = '{indicator.value}']",
                'labels': [t.value for t in indicator.threat_types],
                'confidence': {'high': 100, 'medium': 70, 'low': 30, 'unknown': 0}.get(indicator.confidence.value, 0)
            }
            stix_objects.append(stix_object)
        
        stix_bundle = {
            'type': 'bundle',
            'id': f'bundle--{hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()}',
            'objects': stix_objects
        }
        
        return json.dumps(stix_bundle, indent=2)
    
    def add_to_whitelist(self, value: str):
        """Add value to whitelist"""
        self.whitelist.add(value)
        self.logger.info(f"Added {value} to whitelist")
    
    def remove_from_whitelist(self, value: str):
        """Remove value from whitelist"""
        if value in self.whitelist:
            self.whitelist.remove(value)
            self.logger.info(f"Removed {value} from whitelist")
    
    def get_whitelist(self) -> List[str]:
        """Get current whitelist"""
        return list(self.whitelist)


# Export main classes
__all__ = ['ThreatIntelligence', 'ThreatIndicator', 'ThreatReport', 'ThreatMatch', 'ThreatType', 'ThreatSeverity', 'IndicatorType', 'Confidence']