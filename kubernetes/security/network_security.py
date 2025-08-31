"""
Advanced Network Security Monitor for Deployment Infrastructure

Provides real-time network security monitoring, intrusion detection,
traffic analysis, and network-based threat prevention for the IA Influencer
Agent platform deployment infrastructure.

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
import socket
import struct
import time
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pcap
import dpkt
import json
import hashlib
import geoip2.database
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class NetworkProtocol(Enum):
    """Network protocol types"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    FTP = "ftp"
    DNS = "dns"
    UNKNOWN = "unknown"


class NetworkThreatType(Enum):
    """Network-specific threat types"""
    PORT_SCAN = "port_scan"
    NETWORK_INTRUSION = "network_intrusion"
    SUSPICIOUS_TRAFFIC = "suspicious_traffic"
    MALICIOUS_PAYLOAD = "malicious_payload"
    BANDWIDTH_ABUSE = "bandwidth_abuse"
    PROTOCOL_ANOMALY = "protocol_anomaly"
    BOTNET_COMMUNICATION = "botnet_communication"
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NetworkConnection:
    """Network connection information"""
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: NetworkProtocol
    bytes_sent: int
    bytes_received: int
    duration: float
    start_time: datetime
    end_time: Optional[datetime] = None
    is_established: bool = False
    is_encrypted: bool = False
    geo_location: Optional[Dict[str, str]] = None


@dataclass
class NetworkPacket:
    """Network packet information"""
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: NetworkProtocol
    payload_size: int
    payload_hash: str
    flags: List[str]
    ttl: int
    packet_id: str


@dataclass
class NetworkAlert:
    """Network security alert"""
    alert_id: str
    threat_type: NetworkThreatType
    severity: AlertSeverity
    source_ip: str
    destination_ip: str
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    confidence_score: float
    is_confirmed: bool = False
    is_resolved: bool = False
    mitigation_actions: List[str] = field(default_factory=list)


@dataclass
class TrafficPattern:
    """Network traffic pattern for analysis"""
    pattern_id: str
    source_ip: str
    destination_ports: Set[int]
    request_frequency: float
    total_bytes: int
    unique_destinations: Set[str]
    time_window: timedelta
    first_seen: datetime
    last_seen: datetime


class PortScanner:
    """
    Port scanning detection system
    """
    
    def __init__(self, scan_threshold: int = 10, time_window: int = 60):
        self.scan_threshold = scan_threshold
        self.time_window = time_window
        
        # Track connection attempts per IP
        self.connection_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Track scanned ports per IP
        self.scanned_ports: Dict[str, Set[int]] = defaultdict(set)
        
        logger.info("Port scanner detector initialized")
    
    def analyze_connection_attempt(
        self,
        source_ip: str,
        destination_port: int,
        timestamp: datetime,
        is_successful: bool
    ) -> Optional[NetworkAlert]:
        """
        Analyze connection attempt for port scanning behavior
        
        Args:
            source_ip: Source IP address
            destination_port: Destination port
            timestamp: Connection timestamp
            is_successful: Whether connection was successful
            
        Returns:
            Alert if port scanning detected
        """



        try:
            current_time = time.time()
            
            # Track connection attempt
            self.connection_attempts[source_ip].append({
                'timestamp': current_time,
                'port': destination_port,
                'successful': is_successful
            })
            
            self.scanned_ports[source_ip].add(destination_port)
            
            # Clean old entries
            cutoff_time = current_time - self.time_window
            while (self.connection_attempts[source_ip] and 
                   self.connection_attempts[source_ip][0]['timestamp'] < cutoff_time):
                old_attempt = self.connection_attempts[source_ip].popleft()
                self.scanned_ports[source_ip].discard(old_attempt['port'])
            
            # Check for port scanning pattern
            recent_attempts = len(self.connection_attempts[source_ip])
            unique_ports = len(self.scanned_ports[source_ip])
            
            if unique_ports >= self.scan_threshold and recent_attempts >= self.scan_threshold:
                # Calculate success rate
                successful_attempts = sum(
                    1 for attempt in self.connection_attempts[source_ip]
                    if attempt['successful']
                )
                success_rate = successful_attempts / recent_attempts if recent_attempts > 0 else 0
                
                # Port scanning detected
                alert = NetworkAlert(
                    alert_id=f"port_scan_{int(current_time)}_{hash(source_ip)}",
                    threat_type=NetworkThreatType.PORT_SCAN,
                    severity=AlertSeverity.HIGH if success_rate < 0.1 else AlertSeverity.MEDIUM,
                    source_ip=source_ip,
                    destination_ip="multiple",
                    description=f"Port scanning activity detected from {source_ip}",
                    evidence={
                        "unique_ports_scanned": unique_ports,
                        "total_attempts": recent_attempts,
                        "success_rate": success_rate,
                        "time_window_seconds": self.time_window,
                        "scanned_ports": list(self.scanned_ports[source_ip])[:20]  # Limit for storage
                    },
                    timestamp=timestamp,
                    confidence_score=min(0.9, unique_ports / 50)  # Higher confidence with more ports
                )
                
                return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze connection attempt: {e}")
            return None


class TrafficAnalyzer:
    """
    Network traffic analysis and anomaly detection
    """
    
    def __init__(self, baseline_window: int = 3600):
        self.baseline_window = baseline_window
        
        # Traffic baselines per IP/port combination
        self.traffic_baselines: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Current traffic metrics
        self.current_metrics: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Traffic patterns
        self.traffic_patterns: Dict[str, TrafficPattern] = {}
        
        logger.info("Traffic analyzer initialized")
    
    def update_traffic_metrics(
        self,
        source_ip: str,
        destination_ip: str,
        destination_port: int,
        bytes_transferred: int,
        timestamp: datetime
    ):
        """
        Update traffic metrics for analysis
        
        Args:
            source_ip: Source IP address
            destination_ip: Destination IP address
            destination_port: Destination port
            bytes_transferred: Number of bytes transferred
            timestamp: Transfer timestamp
        """



        try:
            key = f"{source_ip}:{destination_port}"
            
            # Update current metrics
            self.current_metrics[key]["bytes_per_hour"] += bytes_transferred
            self.current_metrics[key]["connections_per_hour"] += 1
            self.current_metrics[key]["last_activity"] = time.time()
            
            # Update traffic pattern
            pattern_key = f"pattern_{source_ip}"
            
            if pattern_key not in self.traffic_patterns:
                self.traffic_patterns[pattern_key] = TrafficPattern(
                    pattern_id=pattern_key,
                    source_ip=source_ip,
                    destination_ports=set(),
                    request_frequency=0.0,
                    total_bytes=0,
                    unique_destinations=set(),
                    time_window=timedelta(hours=1),
                    first_seen=timestamp,
                    last_seen=timestamp
                )
            
            pattern = self.traffic_patterns[pattern_key]
            pattern.destination_ports.add(destination_port)
            pattern.unique_destinations.add(destination_ip)
            pattern.total_bytes += bytes_transferred
            pattern.last_seen = timestamp
            
        except Exception as e:
            logger.error(f"Failed to update traffic metrics: {e}")
    
    def detect_traffic_anomalies(self, threshold_multiplier: float = 3.0) -> List[NetworkAlert]:
        """
        Detect traffic anomalies based on baseline comparison
        
        Args:
            threshold_multiplier: Multiplier for anomaly threshold
            
        Returns:
            List of traffic anomaly alerts
        """



        try:
            alerts = []
            current_time = time.time()
            
            for key, metrics in self.current_metrics.items():
                # Skip if no recent activity
                if current_time - metrics.get("last_activity", 0) > 3600:
                    continue
                
                baseline = self.traffic_baselines.get(key, {})
                
                # Check for bandwidth anomalies
                current_bandwidth = metrics.get("bytes_per_hour", 0)
                baseline_bandwidth = baseline.get("bytes_per_hour", current_bandwidth)
                
                if baseline_bandwidth > 0:
                    bandwidth_ratio = current_bandwidth / baseline_bandwidth
                    
                    if bandwidth_ratio > threshold_multiplier:
                        source_ip = key.split(':')[0]
                        
                        alert = NetworkAlert(
                            alert_id=f"bandwidth_anomaly_{int(current_time)}_{hash(key)}",
                            threat_type=NetworkThreatType.BANDWIDTH_ABUSE,
                            severity=AlertSeverity.HIGH if bandwidth_ratio > 10 else AlertSeverity.MEDIUM,
                            source_ip=source_ip,
                            destination_ip="multiple",
                            description=f"Unusual bandwidth usage detected from {source_ip}",
                            evidence={
                                "current_bandwidth_bytes": current_bandwidth,
                                "baseline_bandwidth_bytes": baseline_bandwidth,
                                "anomaly_ratio": bandwidth_ratio,
                                "threshold_multiplier": threshold_multiplier
                            },
                            timestamp=datetime.utcnow(),
                            confidence_score=min(0.9, bandwidth_ratio / 10)
                        )
                        
                        alerts.append(alert)
                
                # Check for connection frequency anomalies
                current_connections = metrics.get("connections_per_hour", 0)
                baseline_connections = baseline.get("connections_per_hour", current_connections)
                
                if baseline_connections > 0:
                    connection_ratio = current_connections / baseline_connections
                    
                    if connection_ratio > threshold_multiplier:
                        source_ip = key.split(':')[0]
                        
                        alert = NetworkAlert(
                            alert_id=f"connection_anomaly_{int(current_time)}_{hash(key)}",
                            threat_type=NetworkThreatType.SUSPICIOUS_TRAFFIC,
                            severity=AlertSeverity.MEDIUM,
                            source_ip=source_ip,
                            destination_ip="multiple",
                            description=f"Unusual connection frequency detected from {source_ip}",
                            evidence={
                                "current_connections": current_connections,
                                "baseline_connections": baseline_connections,
                                "anomaly_ratio": connection_ratio,
                                "threshold_multiplier": threshold_multiplier
                            },
                            timestamp=datetime.utcnow(),
                            confidence_score=min(0.8, connection_ratio / 5)
                        )
                        
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to detect traffic anomalies: {e}")
            return []
    
    def update_baselines(self):
        """Update traffic baselines from current metrics"""



        try:
            for key, metrics in self.current_metrics.items():
                # Update baseline with exponential moving average
                alpha = 0.1  # Learning rate
                
                for metric_name, current_value in metrics.items():
                    if metric_name == "last_activity":
                        continue
                        
                    baseline_value = self.traffic_baselines[key].get(metric_name, current_value)
                    self.traffic_baselines[key][metric_name] = (
                        alpha * current_value + (1 - alpha) * baseline_value
                    )
            
            # Reset current metrics
            self.current_metrics.clear()
            
            logger.debug("Traffic baselines updated")
            
        except Exception as e:
            logger.error(f"Failed to update baselines: {e}")


class IntrusionDetector:
    """
    Network intrusion detection system
    """
    
    def __init__(self):
        self.malicious_signatures = self._load_malicious_signatures()
        self.suspicious_user_agents = self._load_suspicious_user_agents()
        self.known_malicious_ips = set()
        
        logger.info("Intrusion detector initialized")
    
    def _load_malicious_signatures(self) -> List[bytes]:
        """Load known malicious payload signatures"""
        # In production, these would be loaded from threat intelligence feeds
        return [
            b"GET /admin",
            b"SELECT * FROM",
            b"<script>",
            b"../../../../etc/passwd",
            b"cmd.exe",
            b"/bin/sh",
            b"wget http://",
            b"curl -O",
            b"nc -l",
            b"rm -rf /",
            b"DROP TABLE",
            b"UNION SELECT",
            b"eval(",
            b"system(",
            b"exec("
        ]
    
    def _load_suspicious_user_agents(self) -> List[str]:
        """Load known suspicious user agents"""



        return [
            "sqlmap",
            "nmap",
            "nikto",
            "dirb",
            "gobuster",
            "masscan",
            "zap",
            "burp",
            "w3af",
            "skipfish",
            "arachni"
        ]
    
    def analyze_packet_payload(
        self,
        packet: NetworkPacket,
        payload: bytes
    ) -> Optional[NetworkAlert]:
        """
        Analyze packet payload for malicious content
        
        Args:
            packet: Network packet information
            payload: Packet payload data
            
        Returns:
            Alert if malicious content detected
        """



        try:
            # Check for malicious signatures
            for signature in self.malicious_signatures:
                if signature in payload.lower():
                    alert = NetworkAlert(
                        alert_id=f"malicious_payload_{int(time.time())}_{packet.packet_id}",
                        threat_type=NetworkThreatType.MALICIOUS_PAYLOAD,
                        severity=AlertSeverity.HIGH,
                        source_ip=packet.source_ip,
                        destination_ip=packet.destination_ip,
                        description=f"Malicious payload detected from {packet.source_ip}",
                        evidence={
                            "signature_matched": signature.decode('utf-8', errors='ignore'),
                            "packet_id": packet.packet_id,
                            "payload_size": len(payload),
                            "destination_port": packet.destination_port
                        },
                        timestamp=packet.timestamp,
                        confidence_score=0.9
                    )
                    
                    return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze packet payload: {e}")
            return None
    
    def analyze_http_request(
        self,
        source_ip: str,
        request_line: str,
        headers: Dict[str, str],
        timestamp: datetime
    ) -> List[NetworkAlert]:
        """
        Analyze HTTP request for suspicious activity
        
        Args:
            source_ip: Source IP address
            request_line: HTTP request line
            headers: HTTP headers
            timestamp: Request timestamp
            
        Returns:
            List of alerts for suspicious activity
        """



        try:
            alerts = []
            
            # Check user agent
            user_agent = headers.get('User-Agent', '').lower()
            for suspicious_agent in self.suspicious_user_agents:
                if suspicious_agent in user_agent:
                    alert = NetworkAlert(
                        alert_id=f"suspicious_ua_{int(time.time())}_{hash(source_ip)}",
                        threat_type=NetworkThreatType.NETWORK_INTRUSION,
                        severity=AlertSeverity.MEDIUM,
                        source_ip=source_ip,
                        destination_ip="web_server",
                        description=f"Suspicious user agent detected from {source_ip}",
                        evidence={
                            "user_agent": user_agent,
                            "suspicious_pattern": suspicious_agent,
                            "request_line": request_line
                        },
                        timestamp=timestamp,
                        confidence_score=0.8
                    )
                    
                    alerts.append(alert)
                    break
            
            # Check for directory traversal attempts
            if "../" in request_line or "..%2F" in request_line:
                alert = NetworkAlert(
                    alert_id=f"directory_traversal_{int(time.time())}_{hash(source_ip)}",
                    threat_type=NetworkThreatType.NETWORK_INTRUSION,
                    severity=AlertSeverity.HIGH,
                    source_ip=source_ip,
                    destination_ip="web_server",
                    description=f"Directory traversal attempt detected from {source_ip}",
                    evidence={
                        "request_line": request_line,
                        "headers": dict(headers)
                    },
                    timestamp=timestamp,
                    confidence_score=0.95
                )
                
                alerts.append(alert)
            
            # Check for SQL injection attempts
            sql_patterns = ["union select", "drop table", "insert into", "delete from", "' or '1'='1"]
            request_lower = request_line.lower()
            
            for pattern in sql_patterns:
                if pattern in request_lower:
                    alert = NetworkAlert(
                        alert_id=f"sql_injection_{int(time.time())}_{hash(source_ip)}",
                        threat_type=NetworkThreatType.MALICIOUS_PAYLOAD,
                        severity=AlertSeverity.HIGH,
                        source_ip=source_ip,
                        destination_ip="web_server",
                        description=f"SQL injection attempt detected from {source_ip}",
                        evidence={
                            "request_line": request_line,
                            "sql_pattern": pattern,
                            "headers": dict(headers)
                        },
                        timestamp=timestamp,
                        confidence_score=0.9
                    )
                    
                    alerts.append(alert)
                    break
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to analyze HTTP request: {e}")
            return []


class NetworkSecurityMonitor:
    """
    Main network security monitoring system
    """
    
    def __init__(
        self,
        interface: str = "eth0",
        redis_url: str = "redis://localhost:6379",
        geoip_db_path: str = None
    ):
        self.interface = interface
        self.redis_url = redis_url
        self.geoip_db_path = geoip_db_path
        
        # Initialize components
        self.port_scanner = PortScanner()
        self.traffic_analyzer = TrafficAnalyzer()
        self.intrusion_detector = IntrusionDetector()
        
        # Network monitoring state
        self.active_connections: Dict[str, NetworkConnection] = {}
        self.network_alerts: List[NetworkAlert] = []
        
        # Geo location analyzer
        self.geo_analyzer = None
        if geoip_db_path:
            try:
                self.geo_analyzer = geoip2.database.Reader(geoip_db_path)
            except Exception as e:
                logger.warning(f"Failed to initialize GeoIP: {e}")
        
        # Redis connection
        self.redis_pool = None
        
        # Monitoring control
        self._monitoring_active = False
        self._monitoring_task = None
        
        logger.info("Network security monitor initialized")
    
    async def initialize_redis(self):
        """Initialize Redis connection"""



        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis connection initialized for network monitoring")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def get_geo_location(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geographic location for IP address"""



        try:
            if not self.geo_analyzer:
                return None
                
            if ipaddress.ip_address(ip_address).is_private:
                return {"country": "Private", "city": "Private Network"}
                
            response = self.geo_analyzer.city(ip_address)
            return {
                "country": response.country.name or "Unknown",
                "city": response.city.name or "Unknown",
                "latitude": float(response.location.latitude or 0),
                "longitude": float(response.location.longitude or 0)
            }
            
        except Exception:
            return None
    
    async def start_monitoring(self):
        """Start network monitoring"""



        try:
            await self.initialize_redis()
            
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info(f"Network monitoring started on interface: {self.interface}")
            
        except Exception as e:
            logger.error(f"Failed to start network monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop network monitoring"""



        try:
            self._monitoring_active = False
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                await self._monitoring_task
            
            logger.info("Network monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop network monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Main network monitoring loop"""



        try:
            # In a real implementation, this would capture network packets
            # For this example, we'll simulate monitoring
            while self._monitoring_active:
                # Simulate packet capture and analysis
                await asyncio.sleep(1)
                
                # Periodically update traffic baselines
                if int(time.time()) % 3600 == 0:  # Every hour
                    self.traffic_analyzer.update_baselines()
                
                # Periodically check for traffic anomalies
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    anomaly_alerts = self.traffic_analyzer.detect_traffic_anomalies()
                    self.network_alerts.extend(anomaly_alerts)
                    
                    # Log alerts
                    for alert in anomaly_alerts:
                        logger.warning(f"Network anomaly detected: {alert.description}")
                
        except asyncio.CancelledError:
            logger.info("Network monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in network monitoring loop: {e}")
    
    def process_network_packet(self, packet_data: bytes) -> List[NetworkAlert]:
        """
        Process captured network packet
        
        Args:
            packet_data: Raw packet data
            
        Returns:
            List of alerts generated from packet analysis
        """



        try:
            alerts = []
            
            # Parse packet (simplified example)
            # In production, this would use proper packet parsing libraries
            packet = self._parse_packet(packet_data)
            
            if not packet:
                return alerts
            
            # Check for port scanning
            if packet.protocol == NetworkProtocol.TCP:
                scan_alert = self.port_scanner.analyze_connection_attempt(
                    source_ip=packet.source_ip,
                    destination_port=packet.destination_port,
                    timestamp=packet.timestamp,
                    is_successful=("ACK" in packet.flags)
                )
                
                if scan_alert:
                    alerts.append(scan_alert)
            
            # Update traffic metrics
            self.traffic_analyzer.update_traffic_metrics(
                source_ip=packet.source_ip,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                bytes_transferred=packet.payload_size,
                timestamp=packet.timestamp
            )
            
            # Analyze payload for malicious content
            if packet.payload_size > 0:
                # This would extract actual payload in production
                simulated_payload = b"GET /admin HTTP/1.1"
                
                payload_alert = self.intrusion_detector.analyze_packet_payload(
                    packet=packet,
                    payload=simulated_payload
                )
                
                if payload_alert:
                    alerts.append(payload_alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to process network packet: {e}")
            return []
    
    def _parse_packet(self, packet_data: bytes) -> Optional[NetworkPacket]:
        """
        Parse raw packet data into NetworkPacket object
        
        Args:
            packet_data: Raw packet data
            
        Returns:
            Parsed packet information
        """



        try:
            # This is a simplified example
            # In production, use proper packet parsing libraries like dpkt or scapy
            
            # Generate mock packet for demonstration
            packet = NetworkPacket(
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.100",
                destination_ip="10.0.0.1",
                source_port=12345,
                destination_port=80,
                protocol=NetworkProtocol.TCP,
                payload_size=len(packet_data),
                payload_hash=hashlib.md5(packet_data).hexdigest(),
                flags=["SYN"],
                ttl=64,
                packet_id=hashlib.sha1(packet_data + str(time.time()).encode()).hexdigest()[:16]
            )
            
            return packet
            
        except Exception as e:
            logger.error(f"Failed to parse packet: {e}")
            return None
    
    def analyze_connection(
        self,
        source_ip: str,
        destination_ip: str,
        destination_port: int,
        protocol: NetworkProtocol,
        bytes_transferred: int
    ) -> List[NetworkAlert]:
        """
        Analyze network connection for security threats
        
        Args:
            source_ip: Source IP address
            destination_ip: Destination IP address
            destination_port: Destination port
            protocol: Network protocol
            bytes_transferred: Number of bytes transferred
            
        Returns:
            List of security alerts
        """



        try:
            alerts = []
            timestamp = datetime.utcnow()
            
            # Create connection key
            conn_key = f"{source_ip}:{destination_ip}:{destination_port}"
            
            # Update or create connection tracking
            if conn_key not in self.active_connections:
                geo_location = self.get_geo_location(source_ip)
                
                self.active_connections[conn_key] = NetworkConnection(
                    source_ip=source_ip,
                    destination_ip=destination_ip,
                    source_port=0,  # Would be extracted from actual packet
                    destination_port=destination_port,
                    protocol=protocol,
                    bytes_sent=bytes_transferred,
                    bytes_received=0,
                    duration=0.0,
                    start_time=timestamp,
                    geo_location=geo_location
                )
            else:
                connection = self.active_connections[conn_key]
                connection.bytes_sent += bytes_transferred
                connection.duration = (timestamp - connection.start_time).total_seconds()
            
            # Check for suspicious geographic locations
            connection = self.active_connections[conn_key]
            if connection.geo_location:
                suspicious_countries = ["Unknown", "North Korea", "Iran"]
                if connection.geo_location.get("country") in suspicious_countries:
                    alert = NetworkAlert(
                        alert_id=f"geo_alert_{int(time.time())}_{hash(source_ip)}",
                        threat_type=NetworkThreatType.SUSPICIOUS_TRAFFIC,
                        severity=AlertSeverity.MEDIUM,
                        source_ip=source_ip,
                        destination_ip=destination_ip,
                        description=f"Connection from suspicious location: {connection.geo_location['country']}",
                        evidence={
                            "country": connection.geo_location.get("country"),
                            "city": connection.geo_location.get("city"),
                            "coordinates": {
                                "lat": connection.geo_location.get("latitude"),
                                "lng": connection.geo_location.get("longitude")
                            }
                        },
                        timestamp=timestamp,
                        confidence_score=0.6
                    )
                    alerts.append(alert)
            
            # Check for data exfiltration (large outbound transfers)
            if bytes_transferred > 100 * 1024 * 1024:  # 100MB threshold
                alert = NetworkAlert(
                    alert_id=f"data_exfil_{int(time.time())}_{hash(conn_key)}",
                    threat_type=NetworkThreatType.DATA_EXFILTRATION,
                    severity=AlertSeverity.HIGH,
                    source_ip=source_ip,
                    destination_ip=destination_ip,
                    description=f"Large data transfer detected: {bytes_transferred} bytes",
                    evidence={
                        "bytes_transferred": bytes_transferred,
                        "destination_port": destination_port,
                        "protocol": protocol.value,
                        "connection_duration": connection.duration
                    },
                    timestamp=timestamp,
                    confidence_score=0.8
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to analyze connection: {e}")
            return []
    
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get current network security status
        
        Returns:
            Network security status summary
        """



        try:
            current_time = datetime.utcnow()
            
            # Count recent alerts by severity
            recent_alerts = [
                alert for alert in self.network_alerts
                if (current_time - alert.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            severity_counts = defaultdict(int)
            threat_type_counts = defaultdict(int)
            
            for alert in recent_alerts:
                severity_counts[alert.severity.value] += 1
                threat_type_counts[alert.threat_type.value] += 1
            
            # Active connections summary
            active_connections_count = len(self.active_connections)
            
            # Top source IPs by connection count
            source_ip_counts = defaultdict(int)
            for connection in self.active_connections.values():
                source_ip_counts[connection.source_ip] += 1
            
            top_sources = sorted(
                source_ip_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "monitoring_active": self._monitoring_active,
                "interface": self.interface,
                "timestamp": current_time.isoformat(),
                "alerts_last_hour": len(recent_alerts),
                "alerts_by_severity": dict(severity_counts),
                "alerts_by_threat_type": dict(threat_type_counts),
                "active_connections": active_connections_count,
                "top_source_ips": top_sources,
                "total_alerts": len(self.network_alerts)
            }
            
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_data(self, retention_hours: int = 24):
        """
        Cleanup old monitoring data
        
        Args:
            retention_hours: Data retention period in hours
        """



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
            
            # Remove old alerts
            self.network_alerts = [
                alert for alert in self.network_alerts
                if alert.timestamp > cutoff_time
            ]
            
            # Remove old connections
            active_connections = {}
            for key, connection in self.active_connections.items():
                if connection.start_time > cutoff_time:
                    active_connections[key] = connection
            
            self.active_connections = active_connections
            
            logger.info(f"Cleaned up monitoring data older than {retention_hours} hours")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Export main classes for module usage
__all__ = [
    'NetworkSecurityMonitor',
    'PortScanner',
    'TrafficAnalyzer',
    'IntrusionDetector',
    'NetworkAlert',
    'NetworkConnection',
    'NetworkPacket',
    'NetworkThreatType',
    'AlertSeverity',
    'NetworkProtocol'
]
