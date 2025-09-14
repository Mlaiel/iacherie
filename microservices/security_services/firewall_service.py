#!/usr/bin/env python3
"""
🛡️ Firewall Service - Enterprise Network Security
Service de pare-feu enterprise pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🛡️ Security Expert Implementation
"""

import asyncio
import logging
import ipaddress
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FirewallAction(Enum):
    """Actions de pare-feu"""
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    REJECT = "reject"
    LOG = "log"
    RATE_LIMIT = "rate_limit"

class ProtocolType(Enum):
    """Types de protocoles"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    ANY = "any"

class ThreatLevel(Enum):
    """Niveaux de menace"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FirewallDirection(Enum):
    """Direction du trafic"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class FirewallRule:
    """Règle de pare-feu"""
    rule_id: str
    name: str
    description: str
    priority: int
    action: FirewallAction
    direction: FirewallDirection
    protocol: ProtocolType
    source_ip: str = "*"
    source_port: str = "*"
    destination_ip: str = "*"
    destination_port: str = "*"
    enabled: bool = True
    rate_limit: Optional[int] = None  # requests per minute
    expire_time: Optional[datetime] = None
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: ThreatLevel
    source_ip: str
    destination_ip: str
    protocol: str
    port: int
    rule_id: str
    action_taken: str
    description: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConnectionStats:
    """Statistiques de connexion"""
    source_ip: str
    destination_ip: str
    protocol: str
    port: int
    connection_count: int = 0
    bytes_transferred: int = 0
    first_seen: datetime = None
    last_seen: datetime = None
    blocked_count: int = 0
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()

@dataclass
class IPReputationData:
    """Données de réputation IP"""
    ip_address: str
    reputation_score: float  # 0-100
    threat_types: List[str]
    country: str
    asn: str
    is_malicious: bool
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class FirewallService:
    """Service de pare-feu Enterprise"""
    
    def __init__(self):
        self.service_name = "firewall-service"
        self.version = "1.0.0"
        
        # Règles de pare-feu
        self.firewall_rules: Dict[str, FirewallRule] = {}
        self.rule_priorities = []
        
        # Monitoring et logging
        self.security_events: List[SecurityEvent] = []
        self.connection_stats: Dict[str, ConnectionStats] = {}
        self.blocked_ips: Set[str] = set()
        self.allowed_ips: Set[str] = set()
        
        # IP Reputation et Threat Intelligence
        self.ip_reputation_cache: Dict[str, IPReputationData] = {}
        self.threat_feeds: List[str] = []
        
        # Rate limiting
        self.rate_limit_counters: Dict[str, Dict[str, int]] = {}
        self.rate_limit_window = 60  # seconds
        
        # Configuration
        self.default_action = FirewallAction.DENY
        self.log_all_traffic = False
        self.geo_blocking_enabled = True
        self.threat_intelligence_enabled = True
        
        # Métriques enterprise
        self.metrics = {
            'total_rules': 0,
            'active_rules': 0,
            'packets_processed': 0,
            'packets_allowed': 0,
            'packets_blocked': 0,
            'threats_detected': 0,
            'security_events': 0,
            'rate_limit_hits': 0,
            'connections_tracked': 0
        }
        
        # Pays bloqués (exemple)
        self.blocked_countries = set()
        
        # Patterns d'attaque connus
        self.attack_patterns = {
            'sql_injection': [
                r"(?i)(\bor\b|\band\b).*?=.*?('|\")",
                r"(?i)union.*?select",
                r"(?i)drop\s+table",
                r"(?i)insert\s+into"
            ],
            'xss': [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"on(load|error|click)="
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"/proc/self/environ"
            ]
        }
        
        logger.info(f"🛡️ {self.service_name} v{self.version} - Initialisation")
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation du service firewall"""
        try:
            logger.info("🚀 Initialisation Firewall Service...")
            
            if config is None:
                config = {}
            
            # Configuration par défaut
            self.default_action = FirewallAction(config.get('default_action', 'deny'))
            self.log_all_traffic = config.get('log_all_traffic', False)
            self.geo_blocking_enabled = config.get('geo_blocking', True)
            self.threat_intelligence_enabled = config.get('threat_intelligence', True)
            
            # Chargement règles par défaut
            await self._load_default_rules()
            
            # Chargement threat feeds
            await self._load_threat_intelligence_feeds()
            
            # Initialisation monitoring
            await self._start_monitoring()
            
            # Démarrage tâches de maintenance
            asyncio.create_task(self._maintenance_loop())
            
            logger.info("✅ Firewall Service initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation firewall: {e}")
            return False
    
    async def _load_default_rules(self):
        """Chargement des règles par défaut"""
        try:
            # Règle: Bloquer trafic malveillant connu
            malicious_rule = FirewallRule(
                rule_id="block_malicious_ips",
                name="Block Malicious IPs",
                description="Block known malicious IP addresses",
                priority=1000,
                action=FirewallAction.DENY,
                direction=FirewallDirection.INBOUND,
                protocol=ProtocolType.ANY,
                tags=["security", "malicious", "auto-generated"]
            )
            
            # Règle: Autoriser trafic interne
            internal_allow_rule = FirewallRule(
                rule_id="allow_internal_traffic",
                name="Allow Internal Traffic", 
                description="Allow traffic from internal networks",
                priority=900,
                action=FirewallAction.ALLOW,
                direction=FirewallDirection.BIDIRECTIONAL,
                protocol=ProtocolType.ANY,
                source_ip="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16",
                tags=["internal", "trusted"]
            )
            
            # Règle: Autoriser HTTPS
            https_rule = FirewallRule(
                rule_id="allow_https",
                name="Allow HTTPS Traffic",
                description="Allow HTTPS traffic on port 443",
                priority=800,
                action=FirewallAction.ALLOW,
                direction=FirewallDirection.INBOUND,
                protocol=ProtocolType.HTTPS,
                destination_port="443",
                tags=["web", "https"]
            )
            
            # Règle: Rate limiting sur HTTP
            http_rate_limit_rule = FirewallRule(
                rule_id="http_rate_limit",
                name="HTTP Rate Limiting",
                description="Rate limit HTTP requests",
                priority=700,
                action=FirewallAction.RATE_LIMIT,
                direction=FirewallDirection.INBOUND,
                protocol=ProtocolType.HTTP,
                destination_port="80,8080",
                rate_limit=1000,  # 1000 requests per minute
                tags=["rate-limiting", "http"]
            )
            
            # Règle: Bloquer pays à risque
            geo_block_rule = FirewallRule(
                rule_id="geo_blocking",
                name="Geographic Blocking",
                description="Block traffic from high-risk countries",
                priority=600,
                action=FirewallAction.DENY,
                direction=FirewallDirection.INBOUND,
                protocol=ProtocolType.ANY,
                tags=["geo-blocking", "countries"]
            )
            
            # Règle: Log tout le trafic SSH
            ssh_log_rule = FirewallRule(
                rule_id="ssh_logging",
                name="SSH Traffic Logging",
                description="Log all SSH connection attempts",
                priority=500,
                action=FirewallAction.LOG,
                direction=FirewallDirection.INBOUND,
                protocol=ProtocolType.TCP,
                destination_port="22",
                tags=["ssh", "logging"]
            )
            
            # Ajout des règles
            rules = [
                malicious_rule, internal_allow_rule, https_rule,
                http_rate_limit_rule, geo_block_rule, ssh_log_rule
            ]
            
            for rule in rules:
                await self.add_firewall_rule(rule)
            
            logger.info(f"✅ {len(rules)} règles par défaut chargées")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement règles par défaut: {e}")
            raise
    
    async def _load_threat_intelligence_feeds(self):
        """Chargement des feeds de threat intelligence"""
        try:
            if not self.threat_intelligence_enabled:
                return
            
            # Feeds publics de réputation IP
            threat_feeds = [
                "https://feodotracker.abuse.ch/downloads/ipblocklist.txt",
                "https://reputation.alienvault.com/reputation.data",
                "https://www.spamhaus.org/drop/drop.txt"
            ]
            
            self.threat_feeds = threat_feeds
            
            # Chargement périodique des feeds
            asyncio.create_task(self._update_threat_feeds())
            
            logger.info(f"✅ {len(threat_feeds)} threat feeds configurés")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement threat feeds: {e}")
            raise
    
    async def _update_threat_feeds(self):
        """Mise à jour des threat feeds"""
        while True:
            try:
                await asyncio.sleep(3600)  # Mise à jour toutes les heures
                
                for feed_url in self.threat_feeds:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                                if response.status == 200:
                                    content = await response.text()
                                    await self._process_threat_feed(content, feed_url)
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur feed {feed_url}: {e}")
                
                logger.info("✅ Threat feeds mis à jour")
                
            except Exception as e:
                logger.error(f"❌ Erreur mise à jour threat feeds: {e}")
    
    async def _process_threat_feed(self, content: str, feed_url: str):
        """Traitement d'un threat feed"""
        try:
            lines = content.split('\n')
            new_malicious_ips = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extraction IP (format varie selon le feed)
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                if ip_match:
                    ip = ip_match.group()
                    
                    # Validation IP
                    try:
                        ipaddress.ip_address(ip)
                        
                        # Ajout à la réputation
                        self.ip_reputation_cache[ip] = IPReputationData(
                            ip_address=ip,
                            reputation_score=0.0,  # Score très bas pour IPs malveillantes
                            threat_types=["malware", "botnet"],
                            country="unknown",
                            asn="unknown",
                            is_malicious=True
                        )
                        
                        self.blocked_ips.add(ip)
                        new_malicious_ips += 1
                        
                    except ValueError:
                        continue
            
            logger.info(f"📊 Feed {feed_url}: {new_malicious_ips} nouvelles IPs malveillantes")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement feed: {e}")
    
    async def add_firewall_rule(self, rule: FirewallRule) -> bool:
        """Ajout d'une règle de pare-feu"""
        try:
            # Validation de la règle
            if not await self._validate_rule(rule):
                logger.error(f"❌ Règle invalide: {rule.rule_id}")
                return False
            
            # Ajout de la règle
            self.firewall_rules[rule.rule_id] = rule
            
            # Mise à jour priorités
            self._update_rule_priorities()
            
            # Mise à jour métriques
            self.metrics['total_rules'] = len(self.firewall_rules)
            self.metrics['active_rules'] = len([
                r for r in self.firewall_rules.values() if r.enabled
            ])
            
            logger.info(f"✅ Règle ajoutée: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout règle: {e}")
            return False
    
    async def _validate_rule(self, rule: FirewallRule) -> bool:
        """Validation d'une règle"""
        try:
            # Vérifier ID unique
            if rule.rule_id in self.firewall_rules:
                logger.warning(f"⚠️ Règle existe déjà: {rule.rule_id}")
                return False
            
            # Validation adresses IP
            if not self._validate_ip_pattern(rule.source_ip):
                logger.error(f"❌ IP source invalide: {rule.source_ip}")
                return False
            
            if not self._validate_ip_pattern(rule.destination_ip):
                logger.error(f"❌ IP destination invalide: {rule.destination_ip}")
                return False
            
            # Validation ports
            if not self._validate_port_pattern(rule.source_port):
                logger.error(f"❌ Port source invalide: {rule.source_port}")
                return False
            
            if not self._validate_port_pattern(rule.destination_port):
                logger.error(f"❌ Port destination invalide: {rule.destination_port}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur validation règle: {e}")
            return False
    
    def _validate_ip_pattern(self, ip_pattern: str) -> bool:
        """Validation d'un pattern IP"""
        if ip_pattern == "*":
            return True
        
        # Support plusieurs IPs séparées par virgules
        ips = ip_pattern.split(',')
        
        for ip in ips:
            ip = ip.strip()
            try:
                # Support CIDR
                if '/' in ip:
                    ipaddress.ip_network(ip, strict=False)
                else:
                    ipaddress.ip_address(ip)
            except ValueError:
                return False
        
        return True
    
    def _validate_port_pattern(self, port_pattern: str) -> bool:
        """Validation d'un pattern de port"""
        if port_pattern == "*":
            return True
        
        # Support plusieurs ports
        ports = port_pattern.split(',')
        
        for port in ports:
            port = port.strip()
            
            # Support ranges (ex: 8000-8080)
            if '-' in port:
                try:
                    start, end = port.split('-')
                    start_port = int(start)
                    end_port = int(end)
                    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                        return False
                    if start_port > end_port:
                        return False
                except ValueError:
                    return False
            else:
                try:
                    port_num = int(port)
                    if not (1 <= port_num <= 65535):
                        return False
                except ValueError:
                    return False
        
        return True
    
    def _update_rule_priorities(self):
        """Mise à jour des priorités de règles"""
        self.rule_priorities = sorted(
            [rule for rule in self.firewall_rules.values() if rule.enabled],
            key=lambda x: x.priority,
            reverse=True
        )
    
    async def process_packet(self, packet_info: Dict[str, Any]) -> Tuple[FirewallAction, str]:
        """Traitement d'un paquet réseau"""
        try:
            source_ip = packet_info.get('source_ip', '')
            destination_ip = packet_info.get('destination_ip', '')
            protocol = packet_info.get('protocol', '').lower()
            destination_port = packet_info.get('destination_port', 0)
            payload = packet_info.get('payload', '')
            
            self.metrics['packets_processed'] += 1
            
            # Vérification réputation IP
            reputation_check = await self._check_ip_reputation(source_ip)
            if reputation_check['is_malicious']:
                await self._log_security_event(
                    "malicious_ip_blocked",
                    ThreatLevel.HIGH,
                    source_ip,
                    destination_ip,
                    protocol,
                    destination_port,
                    "Blocked malicious IP from threat intelligence"
                )
                self.metrics['threats_detected'] += 1
                self.metrics['packets_blocked'] += 1
                return FirewallAction.DENY, "Malicious IP detected"
            
            # Vérification geo-blocking
            if self.geo_blocking_enabled:
                geo_check = await self._check_geographic_restrictions(source_ip)
                if not geo_check['allowed']:
                    await self._log_security_event(
                        "geo_blocked",
                        ThreatLevel.MEDIUM,
                        source_ip,
                        destination_ip,
                        protocol,
                        destination_port,
                        f"Blocked traffic from {geo_check['country']}"
                    )
                    self.metrics['packets_blocked'] += 1
                    return FirewallAction.DENY, f"Geographic restriction: {geo_check['country']}"
            
            # Détection d'attaques dans le payload
            attack_detected = await self._detect_attacks_in_payload(payload)
            if attack_detected['is_attack']:
                await self._log_security_event(
                    "attack_detected",
                    ThreatLevel.CRITICAL,
                    source_ip,
                    destination_ip,
                    protocol,
                    destination_port,
                    f"Attack detected: {attack_detected['attack_type']}"
                )
                self.metrics['threats_detected'] += 1
                self.metrics['packets_blocked'] += 1
                return FirewallAction.DENY, f"Attack detected: {attack_detected['attack_type']}"
            
            # Application des règles de pare-feu
            for rule in self.rule_priorities:
                if await self._matches_rule(rule, packet_info):
                    action = await self._apply_rule_action(rule, packet_info)
                    
                    # Logging si requis
                    if action in [FirewallAction.DENY, FirewallAction.DROP] or rule.action == FirewallAction.LOG:
                        await self._log_security_event(
                            "firewall_rule_applied",
                            ThreatLevel.LOW if action == FirewallAction.ALLOW else ThreatLevel.MEDIUM,
                            source_ip,
                            destination_ip,
                            protocol,
                            destination_port,
                            f"Rule {rule.rule_id} applied: {action.value}"
                        )
                    
                    # Mise à jour métriques
                    if action == FirewallAction.ALLOW:
                        self.metrics['packets_allowed'] += 1
                    else:
                        self.metrics['packets_blocked'] += 1
                    
                    # Mise à jour statistiques de connexion
                    await self._update_connection_stats(packet_info, action)
                    
                    return action, f"Rule {rule.rule_id}: {rule.name}"
            
            # Action par défaut
            if self.default_action == FirewallAction.ALLOW:
                self.metrics['packets_allowed'] += 1
            else:
                self.metrics['packets_blocked'] += 1
            
            return self.default_action, "Default action"
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement paquet: {e}")
            return FirewallAction.DENY, "Processing error"
    
    async def _check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Vérification de réputation IP"""
        try:
            # Vérifier cache local
            if ip in self.ip_reputation_cache:
                rep_data = self.ip_reputation_cache[ip]
                return {
                    'is_malicious': rep_data.is_malicious,
                    'reputation_score': rep_data.reputation_score,
                    'threat_types': rep_data.threat_types
                }
            
            # Vérifier listes bloquées
            if ip in self.blocked_ips:
                return {
                    'is_malicious': True,
                    'reputation_score': 0.0,
                    'threat_types': ['blocklist']
                }
            
            # Vérifier listes autorisées
            if ip in self.allowed_ips:
                return {
                    'is_malicious': False,
                    'reputation_score': 100.0,
                    'threat_types': []
                }
            
            # IP inconnue - Score neutre
            return {
                'is_malicious': False,
                'reputation_score': 50.0,
                'threat_types': []
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification réputation IP: {e}")
            return {
                'is_malicious': False,
                'reputation_score': 50.0,
                'threat_types': []
            }
    
    async def _check_geographic_restrictions(self, ip: str) -> Dict[str, Any]:
        """Vérification des restrictions géographiques"""
        try:
            # Simulation géolocalisation (en production, utiliser MaxMind GeoIP)
            # Pour l'exemple, blocage simulé
            blocked_countries = {'CN', 'RU', 'KP', 'IR'}
            
            # Simulation lookup pays
            import random
            countries = ['US', 'DE', 'FR', 'GB', 'JP', 'CN', 'RU']
            simulated_country = random.choice(countries)
            
            is_blocked = simulated_country in blocked_countries
            
            return {
                'allowed': not is_blocked,
                'country': simulated_country,
                'reason': 'High-risk country' if is_blocked else 'Allowed country'
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification géographique: {e}")
            return {
                'allowed': True,
                'country': 'unknown',
                'reason': 'Geolocation failed'
            }
    
    async def _detect_attacks_in_payload(self, payload: str) -> Dict[str, Any]:
        """Détection d'attaques dans le payload"""
        try:
            if not payload:
                return {'is_attack': False, 'attack_type': None}
            
            # Vérification des patterns d'attaque
            for attack_type, patterns in self.attack_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, payload):
                        return {
                            'is_attack': True,
                            'attack_type': attack_type,
                            'pattern_matched': pattern
                        }
            
            return {'is_attack': False, 'attack_type': None}
            
        except Exception as e:
            logger.error(f"❌ Erreur détection attaques: {e}")
            return {'is_attack': False, 'attack_type': None}
    
    async def _matches_rule(self, rule: FirewallRule, packet_info: Dict[str, Any]) -> bool:
        """Vérification si un paquet correspond à une règle"""
        try:
            source_ip = packet_info.get('source_ip', '')
            destination_ip = packet_info.get('destination_ip', '')
            protocol = packet_info.get('protocol', '').lower()
            source_port = packet_info.get('source_port', 0)
            destination_port = packet_info.get('destination_port', 0)
            direction = packet_info.get('direction', 'inbound')
            
            # Vérification direction
            if rule.direction != FirewallDirection.BIDIRECTIONAL:
                if rule.direction.value != direction:
                    return False
            
            # Vérification protocole
            if rule.protocol != ProtocolType.ANY:
                if rule.protocol.value != protocol:
                    return False
            
            # Vérification IP source
            if not self._ip_matches_pattern(source_ip, rule.source_ip):
                return False
            
            # Vérification IP destination
            if not self._ip_matches_pattern(destination_ip, rule.destination_ip):
                return False
            
            # Vérification port source
            if not self._port_matches_pattern(source_port, rule.source_port):
                return False
            
            # Vérification port destination
            if not self._port_matches_pattern(destination_port, rule.destination_port):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur correspondance règle: {e}")
            return False
    
    def _ip_matches_pattern(self, ip: str, pattern: str) -> bool:
        """Vérification correspondance IP avec pattern"""
        if pattern == "*":
            return True
        
        try:
            ip_addr = ipaddress.ip_address(ip)
            patterns = pattern.split(',')
            
            for p in patterns:
                p = p.strip()
                if '/' in p:
                    # CIDR
                    network = ipaddress.ip_network(p, strict=False)
                    if ip_addr in network:
                        return True
                else:
                    # IP exacte
                    if str(ip_addr) == p:
                        return True
            
            return False
            
        except ValueError:
            return False
    
    def _port_matches_pattern(self, port: int, pattern: str) -> bool:
        """Vérification correspondance port avec pattern"""
        if pattern == "*":
            return True
        
        try:
            patterns = pattern.split(',')
            
            for p in patterns:
                p = p.strip()
                if '-' in p:
                    # Range
                    start, end = p.split('-')
                    if int(start) <= port <= int(end):
                        return True
                else:
                    # Port exact
                    if int(p) == port:
                        return True
            
            return False
            
        except ValueError:
            return False
    
    async def _apply_rule_action(self, rule: FirewallRule, packet_info: Dict[str, Any]) -> FirewallAction:
        """Application de l'action d'une règle"""
        try:
            action = rule.action
            
            # Gestion rate limiting
            if action == FirewallAction.RATE_LIMIT and rule.rate_limit:
                source_ip = packet_info.get('source_ip', '')
                
                if await self._check_rate_limit(source_ip, rule.rate_limit):
                    return FirewallAction.ALLOW
                else:
                    self.metrics['rate_limit_hits'] += 1
                    return FirewallAction.DENY
            
            return action
            
        except Exception as e:
            logger.error(f"❌ Erreur application action: {e}")
            return FirewallAction.DENY
    
    async def _check_rate_limit(self, source_ip: str, limit: int) -> bool:
        """Vérification rate limiting"""
        try:
            current_time = int(time.time())
            window_start = current_time - (current_time % self.rate_limit_window)
            
            if source_ip not in self.rate_limit_counters:
                self.rate_limit_counters[source_ip] = {}
            
            counter = self.rate_limit_counters[source_ip]
            
            # Nettoyage des anciennes fenêtres
            old_windows = [w for w in counter.keys() if w < window_start - self.rate_limit_window]
            for w in old_windows:
                del counter[w]
            
            # Vérification limite actuelle
            current_count = counter.get(window_start, 0)
            
            if current_count >= limit:
                return False
            
            # Incrément compteur
            counter[window_start] = current_count + 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur rate limit check: {e}")
            return False
    
    async def _update_connection_stats(self, packet_info: Dict[str, Any], action: FirewallAction):
        """Mise à jour statistiques de connexion"""
        try:
            source_ip = packet_info.get('source_ip', '')
            destination_ip = packet_info.get('destination_ip', '')
            protocol = packet_info.get('protocol', '')
            port = packet_info.get('destination_port', 0)
            
            stats_key = f"{source_ip}:{destination_ip}:{protocol}:{port}"
            
            if stats_key not in self.connection_stats:
                self.connection_stats[stats_key] = ConnectionStats(
                    source_ip=source_ip,
                    destination_ip=destination_ip,
                    protocol=protocol,
                    port=port
                )
            
            stats = self.connection_stats[stats_key]
            stats.connection_count += 1
            stats.last_seen = datetime.now()
            stats.bytes_transferred += packet_info.get('size', 0)
            
            if action in [FirewallAction.DENY, FirewallAction.DROP]:
                stats.blocked_count += 1
            
            self.metrics['connections_tracked'] = len(self.connection_stats)
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour stats connexion: {e}")
    
    async def _log_security_event(self, 
                                event_type: str,
                                severity: ThreatLevel,
                                source_ip: str,
                                destination_ip: str,
                                protocol: str,
                                port: int,
                                description: str):
        """Logging d'un événement de sécurité"""
        try:
            event = SecurityEvent(
                event_id=f"fw_{int(time.time())}_{len(self.security_events)}",
                timestamp=datetime.now(),
                event_type=event_type,
                severity=severity,
                source_ip=source_ip,
                destination_ip=destination_ip,
                protocol=protocol,
                port=port,
                rule_id="",
                action_taken=event_type,
                description=description
            )
            
            self.security_events.append(event)
            self.metrics['security_events'] += 1
            
            # Nettoyage périodique des événements
            if len(self.security_events) > 10000:
                self.security_events = self.security_events[-5000:]
            
            # Log selon la sévérité
            if severity == ThreatLevel.CRITICAL:
                logger.critical(f"🚨 CRITIQUE: {description} - {source_ip} → {destination_ip}:{port}")
            elif severity == ThreatLevel.HIGH:
                logger.error(f"🔴 ÉLEVÉ: {description} - {source_ip} → {destination_ip}:{port}")
            elif severity == ThreatLevel.MEDIUM:
                logger.warning(f"🟠 MOYEN: {description} - {source_ip} → {destination_ip}:{port}")
            else:
                logger.info(f"🟢 INFO: {description} - {source_ip} → {destination_ip}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Erreur logging événement sécurité: {e}")
    
    async def _start_monitoring(self):
        """Démarrage du monitoring"""
        try:
            asyncio.create_task(self._monitoring_loop())
            logger.info("✅ Monitoring firewall démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage monitoring: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitoring toutes les minutes
                
                # Analyse des patterns de trafic
                await self._analyze_traffic_patterns()
                
                # Détection d'anomalies
                await self._detect_anomalies()
                
                # Nettoyage des données anciennes
                await self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle monitoring: {e}")
    
    async def _analyze_traffic_patterns(self):
        """Analyse des patterns de trafic"""
        try:
            # Analyse des connexions par IP source
            ip_connections = {}
            for stats in self.connection_stats.values():
                ip = stats.source_ip
                ip_connections[ip] = ip_connections.get(ip, 0) + stats.connection_count
            
            # Détection de scan de ports potentiel
            for ip, count in ip_connections.items():
                if count > 100:  # Seuil configurable
                    await self._log_security_event(
                        "potential_port_scan",
                        ThreatLevel.MEDIUM,
                        ip,
                        "",
                        "tcp",
                        0,
                        f"Potential port scan detected: {count} connections from {ip}"
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns: {e}")
    
    async def _detect_anomalies(self):
        """Détection d'anomalies"""
        try:
            current_time = datetime.now()
            
            # Anomalie: Trafic inhabituellement élevé
            recent_events = [
                e for e in self.security_events
                if (current_time - e.timestamp).total_seconds() < 300  # 5 minutes
            ]
            
            if len(recent_events) > 50:  # Seuil configurable
                logger.warning(f"🚨 Anomalie détectée: {len(recent_events)} événements en 5 minutes")
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies: {e}")
    
    async def _cleanup_old_data(self):
        """Nettoyage des données anciennes"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=24)
            
            # Nettoyage statistiques de connexion anciennes
            old_stats = []
            for key, stats in self.connection_stats.items():
                if stats.last_seen < cutoff_time:
                    old_stats.append(key)
            
            for key in old_stats:
                del self.connection_stats[key]
            
            # Nettoyage événements anciens
            self.security_events = [
                e for e in self.security_events
                if (current_time - e.timestamp).total_seconds() < 86400  # 24 heures
            ]
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage données: {e}")
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                # Nettoyage rate limiting
                await self._cleanup_rate_limit_counters()
                
                # Vérification règles expirées
                await self._check_expired_rules()
                
                # Export métriques
                await self._export_metrics()
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle maintenance: {e}")
    
    async def _cleanup_rate_limit_counters(self):
        """Nettoyage compteurs rate limiting"""
        try:
            current_time = int(time.time())
            cutoff_time = current_time - (2 * self.rate_limit_window)
            
            for ip in list(self.rate_limit_counters.keys()):
                counter = self.rate_limit_counters[ip]
                
                # Supprimer anciennes fenêtres
                old_windows = [w for w in counter.keys() if w < cutoff_time]
                for w in old_windows:
                    del counter[w]
                
                # Supprimer IPs sans compteurs actifs
                if not counter:
                    del self.rate_limit_counters[ip]
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage rate limit: {e}")
    
    async def _check_expired_rules(self):
        """Vérification des règles expirées"""
        try:
            current_time = datetime.now()
            expired_rules = []
            
            for rule_id, rule in self.firewall_rules.items():
                if rule.expire_time and current_time > rule.expire_time:
                    expired_rules.append(rule_id)
            
            for rule_id in expired_rules:
                del self.firewall_rules[rule_id]
                logger.info(f"🗑️ Règle expirée supprimée: {rule_id}")
            
            if expired_rules:
                self._update_rule_priorities()
                self.metrics['total_rules'] = len(self.firewall_rules)
                self.metrics['active_rules'] = len([
                    r for r in self.firewall_rules.values() if r.enabled
                ])
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification règles expirées: {e}")
    
    async def _export_metrics(self):
        """Export des métriques"""
        try:
            # En production, export vers Prometheus
            logger.debug(f"📊 Métriques firewall: {self.metrics}")
            
        except Exception as e:
            logger.error(f"❌ Erreur export métriques: {e}")
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Dashboard sécurité"""
        try:
            current_time = datetime.now()
            
            # Événements récents
            recent_events = [
                e for e in self.security_events
                if (current_time - e.timestamp).total_seconds() < 3600  # 1 heure
            ]
            
            # Analyse par sévérité
            events_by_severity = {}
            for event in recent_events:
                severity = event.severity.value
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
            
            # Top IPs sources
            ip_counts = {}
            for stats in self.connection_stats.values():
                ip = stats.source_ip
                ip_counts[ip] = ip_counts.get(ip, 0) + stats.connection_count
            
            top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Statistiques règles
            rule_stats = {
                'total_rules': len(self.firewall_rules),
                'active_rules': len([r for r in self.firewall_rules.values() if r.enabled]),
                'rules_by_action': {},
                'rules_by_protocol': {}
            }
            
            for rule in self.firewall_rules.values():
                action = rule.action.value
                protocol = rule.protocol.value
                
                rule_stats['rules_by_action'][action] = rule_stats['rules_by_action'].get(action, 0) + 1
                rule_stats['rules_by_protocol'][protocol] = rule_stats['rules_by_protocol'].get(protocol, 0) + 1
            
            return {
                'timestamp': current_time.isoformat(),
                'metrics': self.metrics,
                'recent_events': {
                    'total': len(recent_events),
                    'by_severity': events_by_severity,
                    'latest': [
                        {
                            'timestamp': e.timestamp.isoformat(),
                            'type': e.event_type,
                            'severity': e.severity.value,
                            'source_ip': e.source_ip,
                            'description': e.description
                        }
                        for e in recent_events[-10:]  # 10 derniers
                    ]
                },
                'traffic_analysis': {
                    'top_source_ips': [
                        {'ip': ip, 'connections': count}
                        for ip, count in top_ips
                    ],
                    'blocked_ips_count': len(self.blocked_ips),
                    'allowed_ips_count': len(self.allowed_ips),
                    'active_connections': len(self.connection_stats)
                },
                'rule_statistics': rule_stats,
                'threat_intelligence': {
                    'reputation_cache_size': len(self.ip_reputation_cache),
                    'malicious_ips_known': len([
                        ip for ip, data in self.ip_reputation_cache.items()
                        if data.is_malicious
                    ]),
                    'threat_feeds_active': len(self.threat_feeds)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur dashboard sécurité: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé firewall"""
        try:
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self.metrics,
                'components': {
                    'rule_engine': len(self.firewall_rules) > 0,
                    'threat_intelligence': self.threat_intelligence_enabled,
                    'geo_blocking': self.geo_blocking_enabled,
                    'rate_limiting': True,
                    'monitoring': True
                },
                'resource_usage': {
                    'rules_loaded': len(self.firewall_rules),
                    'active_connections': len(self.connection_stats),
                    'events_logged': len(self.security_events),
                    'reputation_cache': len(self.ip_reputation_cache)
                }
            }
            
            # Vérifications santé
            checks = {
                'rules_functional': len(self.firewall_rules) > 0,
                'monitoring_active': True,
                'threat_feeds_updated': len(self.ip_reputation_cache) > 0,
                'memory_usage_ok': len(self.security_events) < 10000
            }
            
            health_status['health_checks'] = checks
            
            # Statut global
            if not all(checks.values()):
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Erreur health check firewall: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé firewall"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'configuration': {
                    'default_action': self.default_action.value,
                    'log_all_traffic': self.log_all_traffic,
                    'geo_blocking_enabled': self.geo_blocking_enabled,
                    'threat_intelligence_enabled': self.threat_intelligence_enabled,
                    'rate_limit_window': self.rate_limit_window
                },
                'performance_metrics': self.metrics,
                'security_overview': await self.get_security_dashboard(),
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut firewall: {e}")
            return {'error': str(e)}

# Instance globale
firewall_service = FirewallService()

async def main():
    """Test du firewall service"""
    try:
        print("🛡️ Test Firewall Service")
        
        # Initialisation
        success = await firewall_service.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test traitement paquet normal
        normal_packet = {
            'source_ip': '192.168.1.100',
            'destination_ip': '10.0.0.50',
            'protocol': 'tcp',
            'source_port': 12345,
            'destination_port': 80,
            'direction': 'inbound',
            'size': 1024,
            'payload': 'GET /api/users HTTP/1.1'
        }
        
        action, reason = await firewall_service.process_packet(normal_packet)
        print(f"🔍 Paquet normal: {action.value} - {reason}")
        
        # Test paquet malveillant
        malicious_packet = {
            'source_ip': '1.2.3.4',  # IP potentiellement malveillante
            'destination_ip': '10.0.0.50',
            'protocol': 'tcp',
            'destination_port': 80,
            'direction': 'inbound',
            'payload': "' OR 1=1; DROP TABLE users; --"  # SQL injection
        }
        
        action, reason = await firewall_service.process_packet(malicious_packet)
        print(f"🚨 Paquet malveillant: {action.value} - {reason}")
        
        # Attendre un peu pour voir les métriques
        await asyncio.sleep(2)
        
        # Dashboard sécurité
        dashboard = await firewall_service.get_security_dashboard()
        print(f"📊 Dashboard: {dashboard}")
        
        print("✅ Test Firewall Service terminé")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())