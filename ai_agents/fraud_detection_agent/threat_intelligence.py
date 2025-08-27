"""
Threat Intelligence Engine - Advanced Threat Detection and Intelligence

Sophisticated threat intelligence system for real-time threat detection, 
analysis, and response coordination in the IA-Influencer ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

import requests
import aiohttp
import numpy as np
import redis.asyncio as aioredis
from sqlalchemy.orm import Session

from ...core.exceptions import ThreatIntelligenceError
from ...utils.network_analyzer import NetworkAnalyzer
from ...data.models.threat_intelligence import ThreatIndicator, ThreatReport
from ...integrations.security_feeds import SecurityFeedManager

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Types of threats that can be detected"""
    MALICIOUS_IP = "malicious_ip"
    SUSPICIOUS_DOMAIN = "suspicious_domain"
    BOTNET_ACTIVITY = "botnet_activity"
    PHISHING_ATTEMPT = "phishing_attempt"
    MALWARE_SIGNATURE = "malware_signature"
    ANOMALOUS_TRAFFIC = "anomalous_traffic"
    CREDENTIAL_STUFFING = "credential_stuffing"
    DDOS_ATTEMPT = "ddos_attempt"
    INSIDER_THREAT = "insider_threat"
    APT_ACTIVITY = "apt_activity"

class ThreatSeverity(Enum):
    """Threat severity levels"""
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

class ThreatConfidence(Enum):
    """Confidence levels for threat assessment"""
    UNKNOWN = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    CONFIRMED = 100

@dataclass
class ThreatIndicator:
    """Individual threat indicator"""
    indicator_type: str
    indicator_value: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: ThreatConfidence
    first_seen: datetime
    last_seen: datetime
    source: str
    description: str
    metadata: Dict[str, Any]

@dataclass
class ThreatAnalysisResult:
    """Comprehensive threat analysis result"""
    threat_level: str
    total_indicators: int
    threat_score: float
    indicators: List[Dict[str, Any]]
    risk_factors: List[str]
    recommended_actions: List[str]
    analysis_metadata: Dict[str, Any]
    geolocation_risks: Dict[str, Any]
    network_risks: Dict[str, Any]

class ThreatIntelligenceEngine:
    """
    Advanced Threat Intelligence Engine
    
    Provides threat detection through:
    - Real-time threat feed integration
    - IP reputation analysis
    - Domain reputation checking
    - Behavioral threat analysis
    - Geolocation risk assessment
    - Network traffic analysis
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.network_analyzer = NetworkAnalyzer()
        self.security_feed_manager = SecurityFeedManager()
        
        # Threat intelligence sources
        self.threat_feeds = {
            'malicious_ips': 'malicious_ip_feeds',
            'suspicious_domains': 'suspicious_domain_feeds',
            'malware_hashes': 'malware_hash_feeds',
            'botnet_ips': 'botnet_ip_feeds'
        }
        
        # Risk scoring weights
        self.risk_weights = {
            ThreatType.MALICIOUS_IP: 0.25,
            ThreatType.SUSPICIOUS_DOMAIN: 0.20,
            ThreatType.BOTNET_ACTIVITY: 0.20,
            ThreatType.PHISHING_ATTEMPT: 0.15,
            ThreatType.MALWARE_SIGNATURE: 0.10,
            ThreatType.ANOMALOUS_TRAFFIC: 0.05,
            ThreatType.CREDENTIAL_STUFFING: 0.05
        }
        
        # Geolocation risk matrix
        self.country_risk_scores = {
            # High-risk countries
            'CN': 0.8, 'RU': 0.8, 'KP': 0.9, 'IR': 0.7,
            # Medium-risk countries
            'BR': 0.5, 'IN': 0.4, 'TR': 0.5,
            # Low-risk countries (examples)
            'US': 0.2, 'GB': 0.2, 'DE': 0.2, 'CA': 0.2,
            'AU': 0.2, 'JP': 0.3, 'KR': 0.3, 'FR': 0.2
        }
        
        # Cache TTL settings
        self.cache_ttl = {
            'ip_reputation': 1800,  # 30 minutes
            'domain_reputation': 3600,  # 1 hour
            'threat_feeds': 7200,  # 2 hours
            'geolocation': 86400  # 24 hours
        }
        
        logger.info("Threat Intelligence Engine initialized successfully")

    async def analyze_threats(
        self,
        user_id: str,
        geolocation: Dict[str, Any],
        device_fingerprint: str,
        platform: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive threat intelligence analysis
        
        Args:
            user_id: User identifier
            geolocation: User geolocation data
            device_fingerprint: Device fingerprint
            platform: Platform name
            additional_context: Additional context data
            
        Returns:
            Comprehensive threat analysis results
        """
        try:
            # Extract analysis targets
            ip_address = geolocation.get('ip_address', '')
            country_code = geolocation.get('country_code', '')
            user_agent = additional_context.get('user_agent', '') if additional_context else ''
            
            # Run parallel threat analyses
            analysis_tasks = await asyncio.gather(
                self._analyze_ip_reputation(ip_address),
                self._analyze_geolocation_risk(geolocation),
                self._analyze_device_threats(device_fingerprint),
                self._analyze_behavioral_threats(user_id, additional_context or {}),
                self._check_threat_feeds(ip_address, user_agent),
                self._analyze_network_patterns(ip_address),
                return_exceptions=True
            )
            
            # Collect analysis results
            ip_analysis = analysis_tasks[0] if not isinstance(analysis_tasks[0], Exception) else {}
            geo_analysis = analysis_tasks[1] if not isinstance(analysis_tasks[1], Exception) else {}
            device_analysis = analysis_tasks[2] if not isinstance(analysis_tasks[2], Exception) else {}
            behavioral_analysis = analysis_tasks[3] if not isinstance(analysis_tasks[3], Exception) else {}
            feed_analysis = analysis_tasks[4] if not isinstance(analysis_tasks[4], Exception) else {}
            network_analysis = analysis_tasks[5] if not isinstance(analysis_tasks[5], Exception) else {}
            
            # Aggregate threat indicators
            all_indicators = []
            all_indicators.extend(ip_analysis.get('indicators', []))
            all_indicators.extend(geo_analysis.get('indicators', []))
            all_indicators.extend(device_analysis.get('indicators', []))
            all_indicators.extend(behavioral_analysis.get('indicators', []))
            all_indicators.extend(feed_analysis.get('indicators', []))
            all_indicators.extend(network_analysis.get('indicators', []))
            
            # Calculate composite threat score
            threat_score = await self._calculate_composite_threat_score({
                'ip': ip_analysis,
                'geolocation': geo_analysis,
                'device': device_analysis,
                'behavioral': behavioral_analysis,
                'feeds': feed_analysis,
                'network': network_analysis
            })
            
            # Determine threat level
            threat_level = self._determine_threat_level(threat_score, all_indicators)
            
            # Extract risk factors
            risk_factors = self._extract_risk_factors({
                'ip': ip_analysis,
                'geolocation': geo_analysis,
                'device': device_analysis,
                'behavioral': behavioral_analysis,
                'feeds': feed_analysis,
                'network': network_analysis
            })
            
            # Generate recommendations
            recommendations = await self._generate_threat_recommendations(
                threat_level, all_indicators, threat_score
            )
            
            # Create analysis result
            result = ThreatAnalysisResult(
                threat_level=threat_level,
                total_indicators=len(all_indicators),
                threat_score=threat_score,
                indicators=[
                    {
                        'type': indicator.get('type', ''),
                        'value': indicator.get('value', ''),
                        'severity': indicator.get('severity', 'LOW'),
                        'confidence': indicator.get('confidence', 'LOW'),
                        'description': indicator.get('description', ''),
                        'source': indicator.get('source', 'unknown')
                    }
                    for indicator in all_indicators
                ],
                risk_factors=risk_factors,
                recommended_actions=recommendations,
                analysis_metadata={
                    'user_id': user_id,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'ip_address': ip_address[:10] + "..." if ip_address else '',  # Partial for privacy
                    'country_code': country_code,
                    'platform': platform
                },
                geolocation_risks=geo_analysis,
                network_risks=network_analysis
            )
            
            # Cache analysis result
            await self._cache_threat_analysis(user_id, result)
            
            # Update threat statistics
            await self._update_threat_statistics(user_id, result)
            
            response = {
                'threat_level': result.threat_level,
                'threat_score': result.threat_score,
                'total_indicators': result.total_indicators,
                'indicators': [
                    {
                        'type': indicator['type'],
                        'severity': indicator['severity'],
                        'confidence': indicator['confidence'],
                        'description': indicator['description']
                    }
                    for indicator in result.indicators[:10]  # Limit for response size
                ],
                'risk_factors': result.risk_factors,
                'recommended_actions': result.recommended_actions,
                'geolocation_risk_score': geo_analysis.get('risk_score', 0.0),
                'network_risk_score': network_analysis.get('risk_score', 0.0)
            }
            
            logger.info(
                f"Threat analysis completed for user {user_id}: "
                f"threat_level={result.threat_level}, score={result.threat_score:.3f}, "
                f"indicators={result.total_indicators}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Threat intelligence analysis failed for user {user_id}: {str(e)}")
            raise ThreatIntelligenceError(f"Threat analysis failed: {str(e)}")

    async def _analyze_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Analyze IP address reputation"""
        try:
            if not ip_address:
                return {'risk_score': 0.0, 'indicators': [], 'reputation': 'UNKNOWN'}
                
            # Check cache first
            cache_key = f"ip_reputation:{hashlib.md5(ip_address.encode()).hexdigest()}"
            cached_result = await self.redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
                
            indicators = []
            risk_factors = []
            
            # Check against malicious IP feeds
            is_malicious = await self._check_malicious_ip_feeds(ip_address)
            if is_malicious:
                indicators.append({
                    'type': 'malicious_ip',
                    'value': ip_address,
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'IP address found in malicious IP feeds',
                    'source': 'threat_feeds'
                })
                risk_factors.append('Known malicious IP address')
                
            # Check for botnet activity
            is_botnet = await self._check_botnet_feeds(ip_address)
            if is_botnet:
                indicators.append({
                    'type': 'botnet_ip',
                    'value': ip_address,
                    'severity': 'HIGH',
                    'confidence': 'MEDIUM',
                    'description': 'IP address associated with botnet activity',
                    'source': 'botnet_feeds'
                })
                risk_factors.append('Botnet-associated IP address')
                
            # Check IP age and ASN reputation
            ip_info = await self._get_ip_information(ip_address)
            if ip_info:
                # Young IP addresses can be suspicious
                if ip_info.get('age_days', 365) < 30:
                    indicators.append({
                        'type': 'new_ip',
                        'value': ip_address,
                        'severity': 'MEDIUM',
                        'confidence': 'MEDIUM',
                        'description': 'Recently allocated IP address',
                        'source': 'ip_analysis'
                    })
                    risk_factors.append('Recently allocated IP address')
                    
                # Check ASN reputation
                asn_reputation = ip_info.get('asn_reputation', 'UNKNOWN')
                if asn_reputation == 'BAD':
                    indicators.append({
                        'type': 'bad_asn',
                        'value': ip_address,
                        'severity': 'MEDIUM',
                        'confidence': 'HIGH',
                        'description': 'IP belongs to ASN with bad reputation',
                        'source': 'asn_analysis'
                    })
                    risk_factors.append('Bad ASN reputation')
                    
            # Calculate IP risk score
            risk_score = min(1.0, len(indicators) * 0.3)
            
            reputation = 'CLEAN'
            if risk_score >= 0.7:
                reputation = 'MALICIOUS'
            elif risk_score >= 0.4:
                reputation = 'SUSPICIOUS'
            elif risk_score >= 0.2:
                reputation = 'QUESTIONABLE'
                
            result = {
                'risk_score': risk_score,
                'indicators': indicators,
                'reputation': reputation,
                'risk_factors': risk_factors,
                'ip_info': ip_info
            }
            
            # Cache result
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl['ip_reputation'], 
                json.dumps(result)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"IP reputation analysis failed for {ip_address}: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'reputation': 'UNKNOWN'}

    async def _analyze_geolocation_risk(self, geolocation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze geolocation-based risks"""
        try:
            country_code = geolocation.get('country_code', '')
            city = geolocation.get('city', '')
            latitude = geolocation.get('latitude', 0)
            longitude = geolocation.get('longitude', 0)
            
            indicators = []
            risk_factors = []
            
            # Country-based risk assessment
            country_risk = self.country_risk_scores.get(country_code, 0.3)
            
            if country_risk >= 0.7:
                indicators.append({
                    'type': 'high_risk_country',
                    'value': country_code,
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': f'High-risk country: {country_code}',
                    'source': 'geolocation_analysis'
                })
                risk_factors.append(f'High-risk country: {country_code}')
            elif country_risk >= 0.5:
                indicators.append({
                    'type': 'medium_risk_country',
                    'value': country_code,
                    'severity': 'MEDIUM',
                    'confidence': 'HIGH',
                    'description': f'Medium-risk country: {country_code}',
                    'source': 'geolocation_analysis'
                })
                risk_factors.append(f'Medium-risk country: {country_code}')
                
            # Check for VPN/Proxy usage
            is_vpn = await self._detect_vpn_proxy(geolocation)
            if is_vpn:
                indicators.append({
                    'type': 'vpn_proxy_usage',
                    'value': geolocation.get('ip_address', ''),
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'VPN or proxy usage detected',
                    'source': 'vpn_detection'
                })
                risk_factors.append('VPN or proxy usage')
                
            # Check for known malicious coordinates
            is_malicious_location = await self._check_malicious_coordinates(latitude, longitude)
            if is_malicious_location:
                indicators.append({
                    'type': 'malicious_coordinates',
                    'value': f'{latitude},{longitude}',
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'Coordinates associated with malicious activity',
                    'source': 'location_intelligence'
                })
                risk_factors.append('Malicious location coordinates')
                
            # Rapid location changes (if historical data available)
            location_velocity = await self._calculate_location_velocity(geolocation)
            if location_velocity > 1000:  # > 1000 km/h (impossible for normal travel)
                indicators.append({
                    'type': 'impossible_travel',
                    'value': f'{location_velocity:.1f} km/h',
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'Impossible travel velocity detected',
                    'source': 'travel_analysis'
                })
                risk_factors.append(f'Impossible travel speed: {location_velocity:.1f} km/h')
                
            # Calculate composite geolocation risk
            geo_risk_score = country_risk
            if indicators:
                geo_risk_score = min(1.0, country_risk + len(indicators) * 0.2)
                
            return {
                'risk_score': geo_risk_score,
                'indicators': indicators,
                'risk_factors': risk_factors,
                'country_risk': country_risk,
                'location_analysis': {
                    'country_code': country_code,
                    'city': city,
                    'vpn_detected': is_vpn,
                    'location_velocity': location_velocity
                }
            }
            
        except Exception as e:
            logger.error(f"Geolocation risk analysis failed: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'risk_factors': []}

    async def _analyze_device_threats(self, device_fingerprint: str) -> Dict[str, Any]:
        """Analyze device-based threats"""
        try:
            indicators = []
            risk_factors = []
            
            if not device_fingerprint:
                return {'risk_score': 0.0, 'indicators': indicators, 'risk_factors': risk_factors}
                
            # Check for known malicious device fingerprints
            is_malicious_device = await self._check_malicious_device_fingerprints(device_fingerprint)
            if is_malicious_device:
                indicators.append({
                    'type': 'malicious_device',
                    'value': device_fingerprint[:20] + '...',  # Truncate for privacy
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'Device fingerprint associated with malicious activity',
                    'source': 'device_intelligence'
                })
                risk_factors.append('Known malicious device fingerprint')
                
            # Check for device spoofing indicators
            spoofing_indicators = await self._detect_device_spoofing(device_fingerprint)
            if spoofing_indicators:
                indicators.append({
                    'type': 'device_spoofing',
                    'value': device_fingerprint[:20] + '...',
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'Device fingerprint spoofing detected',
                    'source': 'spoofing_detection'
                })
                risk_factors.append('Possible device fingerprint spoofing')
                
            # Check device consistency across sessions
            consistency_score = await self._analyze_device_consistency(device_fingerprint)
            if consistency_score < 0.3:
                indicators.append({
                    'type': 'device_inconsistency',
                    'value': device_fingerprint[:20] + '...',
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'Inconsistent device characteristics',
                    'source': 'device_analysis'
                })
                risk_factors.append('Inconsistent device characteristics')
                
            device_risk_score = min(1.0, len(indicators) * 0.3)
            
            return {
                'risk_score': device_risk_score,
                'indicators': indicators,
                'risk_factors': risk_factors,
                'device_analysis': {
                    'consistency_score': consistency_score,
                    'spoofing_detected': len(spoofing_indicators) > 0,
                    'malicious_device': is_malicious_device
                }
            }
            
        except Exception as e:
            logger.error(f"Device threat analysis failed: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'risk_factors': []}

    async def _analyze_behavioral_threats(
        self, 
        user_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze behavioral threat patterns"""
        try:
            indicators = []
            risk_factors = []
            
            # Check for credential stuffing patterns
            is_credential_stuffing = await self._detect_credential_stuffing(user_id, context)
            if is_credential_stuffing:
                indicators.append({
                    'type': 'credential_stuffing',
                    'value': user_id,
                    'severity': 'HIGH',
                    'confidence': 'MEDIUM',
                    'description': 'Credential stuffing attack pattern detected',
                    'source': 'behavioral_analysis'
                })
                risk_factors.append('Credential stuffing attack pattern')
                
            # Check for automated behavior patterns
            is_automated = await self._detect_automated_behavior(context)
            if is_automated:
                indicators.append({
                    'type': 'automated_behavior',
                    'value': user_id,
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'Automated behavior patterns detected',
                    'source': 'behavioral_analysis'
                })
                risk_factors.append('Automated behavior patterns')
                
            # Check for insider threat indicators
            insider_risk = await self._assess_insider_threat_risk(user_id, context)
            if insider_risk > 0.6:
                indicators.append({
                    'type': 'insider_threat',
                    'value': user_id,
                    'severity': 'HIGH',
                    'confidence': 'MEDIUM',
                    'description': 'Insider threat risk indicators detected',
                    'source': 'insider_threat_analysis'
                })
                risk_factors.append('Elevated insider threat risk')
                
            behavioral_risk_score = min(1.0, len(indicators) * 0.25 + insider_risk * 0.3)
            
            return {
                'risk_score': behavioral_risk_score,
                'indicators': indicators,
                'risk_factors': risk_factors,
                'behavioral_analysis': {
                    'credential_stuffing_detected': is_credential_stuffing,
                    'automated_behavior_detected': is_automated,
                    'insider_threat_risk': insider_risk
                }
            }
            
        except Exception as e:
            logger.error(f"Behavioral threat analysis failed for user {user_id}: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'risk_factors': []}

    async def _check_threat_feeds(self, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Check against various threat intelligence feeds"""
        try:
            indicators = []
            risk_factors = []
            
            # Check multiple threat feeds in parallel
            feed_tasks = await asyncio.gather(
                self._check_malicious_ip_feeds(ip_address),
                self._check_botnet_feeds(ip_address),
                self._check_malware_user_agents(user_agent),
                return_exceptions=True
            )
            
            malicious_ip = feed_tasks[0] if not isinstance(feed_tasks[0], Exception) else False
            botnet_ip = feed_tasks[1] if not isinstance(feed_tasks[1], Exception) else False
            malware_ua = feed_tasks[2] if not isinstance(feed_tasks[2], Exception) else False
            
            if malicious_ip:
                indicators.append({
                    'type': 'threat_feed_match',
                    'value': ip_address,
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'IP address found in threat intelligence feeds',
                    'source': 'external_feeds'
                })
                risk_factors.append('Threat intelligence feed match')
                
            if botnet_ip:
                indicators.append({
                    'type': 'botnet_feed_match',
                    'value': ip_address,
                    'severity': 'HIGH',
                    'confidence': 'HIGH',
                    'description': 'IP address found in botnet feeds',
                    'source': 'botnet_feeds'
                })
                risk_factors.append('Botnet feed match')
                
            if malware_ua:
                indicators.append({
                    'type': 'malware_user_agent',
                    'value': user_agent[:50] + '...' if len(user_agent) > 50 else user_agent,
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'User agent associated with malware',
                    'source': 'malware_feeds'
                })
                risk_factors.append('Malware-associated user agent')
                
            feed_risk_score = min(1.0, len(indicators) * 0.4)
            
            return {
                'risk_score': feed_risk_score,
                'indicators': indicators,
                'risk_factors': risk_factors,
                'feed_matches': {
                    'malicious_ip': malicious_ip,
                    'botnet_ip': botnet_ip,
                    'malware_user_agent': malware_ua
                }
            }
            
        except Exception as e:
            logger.error(f"Threat feed checking failed: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'risk_factors': []}

    async def _analyze_network_patterns(self, ip_address: str) -> Dict[str, Any]:
        """Analyze network traffic patterns for threats"""
        try:
            indicators = []
            risk_factors = []
            
            # Analyze network behavior patterns
            network_analysis = await self.network_analyzer.analyze_ip_patterns(ip_address)
            
            # Check for DDoS patterns
            if network_analysis.get('ddos_indicators', False):
                indicators.append({
                    'type': 'ddos_pattern',
                    'value': ip_address,
                    'severity': 'HIGH',
                    'confidence': 'MEDIUM',
                    'description': 'DDoS attack patterns detected',
                    'source': 'network_analysis'
                })
                risk_factors.append('DDoS attack patterns')
                
            # Check for port scanning activity
            if network_analysis.get('port_scanning', False):
                indicators.append({
                    'type': 'port_scanning',
                    'value': ip_address,
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'Port scanning activity detected',
                    'source': 'network_analysis'
                })
                risk_factors.append('Port scanning activity')
                
            # Check for unusual traffic volume
            traffic_volume = network_analysis.get('traffic_volume_score', 0.0)
            if traffic_volume > 0.8:
                indicators.append({
                    'type': 'unusual_traffic_volume',
                    'value': ip_address,
                    'severity': 'MEDIUM',
                    'confidence': 'MEDIUM',
                    'description': 'Unusual network traffic volume',
                    'source': 'traffic_analysis'
                })
                risk_factors.append('Unusual traffic volume')
                
            network_risk_score = min(1.0, len(indicators) * 0.3 + traffic_volume * 0.2)
            
            return {
                'risk_score': network_risk_score,
                'indicators': indicators,
                'risk_factors': risk_factors,
                'network_analysis': network_analysis
            }
            
        except Exception as e:
            logger.error(f"Network pattern analysis failed: {str(e)}")
            return {'risk_score': 0.0, 'indicators': [], 'risk_factors': []}

    async def _calculate_composite_threat_score(self, analysis_results: Dict[str, Dict]) -> float:
        """Calculate composite threat score from all analysis methods"""
        weights = {
            'ip': 0.25,
            'geolocation': 0.20,
            'device': 0.15,
            'behavioral': 0.20,
            'feeds': 0.15,
            'network': 0.05
        }
        
        composite_score = 0.0
        total_weight = 0.0
        
        for category, weight in weights.items():
            if category in analysis_results:
                category_score = analysis_results[category].get('risk_score', 0.0)
                composite_score += category_score * weight
                total_weight += weight
                
        # Normalize by actual weights used
        if total_weight > 0:
            composite_score = composite_score / total_weight
            
        return min(1.0, composite_score)

    def _determine_threat_level(self, threat_score: float, indicators: List[Dict]) -> str:
        """Determine overall threat level"""
        critical_indicators = [
            'malicious_ip', 'botnet_ip', 'malicious_device', 
            'credential_stuffing', 'insider_threat'
        ]
        
        has_critical_indicator = any(
            indicator.get('type') in critical_indicators and indicator.get('severity') == 'HIGH'
            for indicator in indicators
        )
        
        if has_critical_indicator or threat_score >= 0.8:
            return 'RED'
        elif threat_score >= 0.6:
            return 'ORANGE'
        elif threat_score >= 0.4:
            return 'YELLOW'
        else:
            return 'GREEN'

    def _extract_risk_factors(self, analysis_results: Dict[str, Dict]) -> List[str]:
        """Extract key risk factors from all analyses"""
        risk_factors = []
        
        for category_results in analysis_results.values():
            category_risks = category_results.get('risk_factors', [])
            risk_factors.extend(category_risks)
            
        # Remove duplicates and limit to top 10
        unique_risks = list(dict.fromkeys(risk_factors))
        return unique_risks[:10]

    async def _generate_threat_recommendations(
        self, 
        threat_level: str, 
        indicators: List[Dict], 
        threat_score: float
    ) -> List[str]:
        """Generate recommended actions based on threat analysis"""
        recommendations = []
        
        if threat_level == 'RED':
            recommendations.extend([
                'Immediately block user access',
                'Initiate incident response procedures',
                'Alert security operations center',
                'Preserve forensic evidence',
                'Block associated IP addresses'
            ])
        elif threat_level == 'ORANGE':
            recommendations.extend([
                'Apply enhanced security monitoring',
                'Require additional authentication',
                'Flag for manual security review',
                'Monitor for pattern escalation'
            ])
        elif threat_level == 'YELLOW':
            recommendations.extend([
                'Increase monitoring frequency',
                'Apply rate limiting',
                'Log all activities for analysis'
            ])
            
        # Specific recommendations based on threat types
        threat_types = {indicator.get('type', '') for indicator in indicators}
        
        if 'credential_stuffing' in threat_types:
            recommendations.append('Implement account lockout policies')
            
        if 'vpn_proxy_usage' in threat_types:
            recommendations.append('Review VPN/proxy usage policies')
            
        if 'device_spoofing' in threat_types:
            recommendations.append('Implement device fingerprint validation')
            
        if 'botnet_ip' in threat_types:
            recommendations.append('Block botnet-associated IP ranges')
            
        return list(set(recommendations))  # Remove duplicates

    # Placeholder implementations for threat detection methods
    async def _check_malicious_ip_feeds(self, ip_address: str) -> bool:
        """Check IP against malicious IP feeds"""
        try:
            # This would integrate with actual threat feeds
            # For now, simulate with some basic checks
            return False  # Most IPs are not malicious
        except:
            return False

    async def _check_botnet_feeds(self, ip_address: str) -> bool:
        """Check IP against botnet feeds"""
        try:
            # This would integrate with botnet threat feeds
            return False
        except:
            return False

    async def _check_malware_user_agents(self, user_agent: str) -> bool:
        """Check user agent against malware signatures"""
        try:
            # Check for known malware user agent patterns
            malware_patterns = ['bot', 'crawler', 'spider', 'scanner']
            return any(pattern in user_agent.lower() for pattern in malware_patterns)
        except:
            return False

    async def _get_ip_information(self, ip_address: str) -> Dict[str, Any]:
        """Get comprehensive IP information"""
        try:
            # This would integrate with IP intelligence services
            return {
                'age_days': 365,
                'asn_reputation': 'GOOD',
                'country': 'Unknown',
                'isp': 'Unknown'
            }
        except:
            return {}

    async def _detect_vpn_proxy(self, geolocation: Dict[str, Any]) -> bool:
        """Detect VPN or proxy usage"""
        try:
            # This would integrate with VPN/proxy detection services
            return False
        except:
            return False

    async def _check_malicious_coordinates(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are associated with malicious activity"""
        try:
            # This would check against databases of known malicious locations
            return False
        except:
            return False

    async def _calculate_location_velocity(self, geolocation: Dict[str, Any]) -> float:
        """Calculate travel velocity between locations"""
        try:
            # This would compare with previous locations to calculate travel speed
            return 0.0  # No velocity calculated
        except:
            return 0.0

    async def _check_malicious_device_fingerprints(self, device_fingerprint: str) -> bool:
        """Check device fingerprint against malicious device database"""
        try:
            # This would check against databases of known malicious devices
            return False
        except:
            return False

    async def _detect_device_spoofing(self, device_fingerprint: str) -> List[str]:
        """Detect device fingerprint spoofing indicators"""
        try:
            # This would analyze device fingerprint for spoofing indicators
            return []
        except:
            return []

    async def _analyze_device_consistency(self, device_fingerprint: str) -> float:
        """Analyze device consistency across sessions"""
        try:
            # This would compare device fingerprints across sessions
            return 0.9  # High consistency by default
        except:
            return 0.5

    async def _detect_credential_stuffing(self, user_id: str, context: Dict[str, Any]) -> bool:
        """Detect credential stuffing attack patterns"""
        try:
            # This would analyze login patterns for credential stuffing
            return False
        except:
            return False

    async def _detect_automated_behavior(self, context: Dict[str, Any]) -> bool:
        """Detect automated behavior patterns"""
        try:
            # This would analyze behavioral patterns for automation
            return False
        except:
            return False

    async def _assess_insider_threat_risk(self, user_id: str, context: Dict[str, Any]) -> float:
        """Assess insider threat risk for user"""
        try:
            # This would analyze user behavior for insider threat indicators
            return 0.1  # Low risk by default
        except:
            return 0.0

    async def _cache_threat_analysis(self, user_id: str, result: ThreatAnalysisResult):
        """Cache threat analysis result"""
        try:
            cache_key = f"threat_analysis:{user_id}"
            
            cached_result = {
                'threat_level': result.threat_level,
                'threat_score': result.threat_score,
                'total_indicators': result.total_indicators,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            await self.redis_client.setex(cache_key, 1800, json.dumps(cached_result))  # 30 minutes
            
        except Exception as e:
            logger.error(f"Failed to cache threat analysis for user {user_id}: {str(e)}")

    async def _update_threat_statistics(self, user_id: str, result: ThreatAnalysisResult):
        """Update threat statistics"""
        try:
            stats_key = f"threat_stats:{result.threat_level}"
            await self.redis_client.hincrby(stats_key, "count", 1)
            await self.redis_client.hset(stats_key, "last_seen", datetime.now().isoformat())
            
        except Exception as e:
            logger.error(f"Failed to update threat statistics: {str(e)}")

    async def update_threat_feeds(self):
        """Update threat intelligence feeds"""
        try:
            # This would update threat feeds from external sources
            await self.security_feed_manager.update_all_feeds()
            logger.info("Threat intelligence feeds updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update threat feeds: {str(e)}")

    async def get_threat_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get threat detection statistics"""
        try:
            stats = {
                'threat_levels': {},
                'total_analyses': 0,
                'top_threat_types': {},
                'geographic_distribution': {}
            }
            
            # Get threat level statistics
            for level in ['RED', 'ORANGE', 'YELLOW', 'GREEN']:
                stats_key = f"threat_stats:{level}"
                count = await self.redis_client.hget(stats_key, "count")
                stats['threat_levels'][level] = int(count) if count else 0
                stats['total_analyses'] += stats['threat_levels'][level]
                
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get threat statistics: {str(e)}")
            return {'error': str(e)}
