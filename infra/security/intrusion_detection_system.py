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

import logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp
import hashlib
import ipaddress
import re
import socket
import subprocess
import threading
from collections import defaultdict, deque
import uuid

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/ainflue/intrusion_detection.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event detected by IDS"""
    event_id: str
    event_type: str  # network_scan, brute_force, malware, suspicious_activity
    severity: str  # low, medium, high, critical
    source_ip: str
    destination_ip: str
    source_port: Optional[int]
    destination_port: Optional[int]
    protocol: str
    timestamp: datetime
    description: str
    raw_data: str
    threat_indicators: List[str]
    confidence_score: float  # 0.0 to 1.0
    blocked: bool
    action_taken: str

@dataclass
class ThreatSignature:
    """Threat detection signature"""
    signature_id: str
    name: str
    description: str
    pattern: str  # regex pattern or rule
    signature_type: str  # network, host, application
    severity: str
    enabled: bool
    last_updated: datetime
    false_positive_rate: float

@dataclass
class NetworkFlow:
    """Network flow data"""
    flow_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    flags: List[str]

class NetworkMonitor:
    """Monitors network traffic for suspicious activities"""
    
    def __init__(self):
        self.monitoring = False
        self.flow_cache = {}
        self.suspicious_ips = set()
        self.rate_limiters = defaultdict(lambda: deque(maxlen=100))
        self.connection_tracking = defaultdict(lambda: {'count': 0, 'last_seen': datetime.utcnow()})
    
    async def start_network_monitoring(self):
        """Start network traffic monitoring"""
        self.monitoring = True
        logger.info("Starting network monitoring")
        
        tasks = [
            self._packet_capture_loop(),
            self._flow_analysis_loop(),
            self._cleanup_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
    
    async def _packet_capture_loop(self):
        """Capture and analyze network packets"""
        while self.monitoring:
            try:
                # This would integrate with packet capture libraries like scapy
                # For now, simulate network flow detection
                await self._simulate_network_flows()
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error in packet capture: {e}")
                await asyncio.sleep(5)
    
    async def _simulate_network_flows(self):
        """Simulate network flow detection for demo purposes"""
        import random
        
        # Generate some simulated network flows
        for _ in range(random.randint(1, 5)):
            flow = NetworkFlow(
                flow_id=str(uuid.uuid4()),
                source_ip=f"192.168.1.{random.randint(1, 254)}",
                destination_ip=f"10.0.0.{random.randint(1, 254)}",
                source_port=random.randint(1024, 65535),
                destination_port=random.choice([22, 80, 443, 3389, 5432]),
                protocol=random.choice(['TCP', 'UDP']),
                bytes_sent=random.randint(100, 10000),
                bytes_received=random.randint(100, 10000),
                packets_sent=random.randint(1, 100),
                packets_received=random.randint(1, 100),
                duration_seconds=random.uniform(0.1, 30.0),
                start_time=datetime.utcnow() - timedelta(seconds=random.randint(1, 60)),
                end_time=datetime.utcnow(),
                flags=['SYN', 'ACK'] if random.choice([True, False]) else ['FIN']
            )
            
            self.flow_cache[flow.flow_id] = flow
            await self._analyze_flow(flow)
    
    async def _analyze_flow(self, flow: NetworkFlow) -> List[SecurityEvent]:
        """Analyze network flow for suspicious patterns"""
        events = []
        
        # Check for port scanning
        if await self._detect_port_scan(flow):
            events.append(await self._create_security_event(
                'port_scan',
                'high',
                flow.source_ip,
                flow.destination_ip,
                flow.source_port,
                flow.destination_port,
                flow.protocol,
                f"Port scanning detected from {flow.source_ip}",
                str(asdict(flow))
            ))
        
        # Check for brute force attacks
        if await self._detect_brute_force(flow):
            events.append(await self._create_security_event(
                'brute_force',
                'critical',
                flow.source_ip,
                flow.destination_ip,
                flow.source_port,
                flow.destination_port,
                flow.protocol,
                f"Brute force attack detected from {flow.source_ip}",
                str(asdict(flow))
            ))
        
        # Check for suspicious data volumes
        if await self._detect_data_exfiltration(flow):
            events.append(await self._create_security_event(
                'data_exfiltration',
                'high',
                flow.source_ip,
                flow.destination_ip,
                flow.source_port,
                flow.destination_port,
                flow.protocol,
                f"Suspicious data transfer detected: {flow.bytes_sent} bytes sent",
                str(asdict(flow))
            ))
        
        return events
    
    async def _detect_port_scan(self, flow: NetworkFlow) -> bool:
        """Detect port scanning patterns"""
        source_ip = flow.source_ip
        current_time = datetime.utcnow()
        
        # Track unique destination ports per source IP
        if source_ip not in self.connection_tracking:
            self.connection_tracking[source_ip] = {
                'ports': set(),
                'first_seen': current_time,
                'last_seen': current_time
            }
        
        tracking = self.connection_tracking[source_ip]
        tracking['ports'].add(flow.destination_port)
        tracking['last_seen'] = current_time
        
        # Consider it a port scan if:
        # 1. More than 10 unique ports accessed within 60 seconds
        # 2. From the same source IP
        time_window = 60  # seconds
        if (len(tracking['ports']) > 10 and 
            (current_time - tracking['first_seen']).total_seconds() < time_window):
            return True
        
        return False
    
    async def _detect_brute_force(self, flow: NetworkFlow) -> bool:
        """Detect brute force attack patterns"""
        # Common brute force target ports
        target_ports = [22, 3389, 21, 23, 80, 443, 993, 995]
        
        if flow.destination_port not in target_ports:
            return False
        
        # Track connection attempts per source IP
        key = f"{flow.source_ip}:{flow.destination_port}"
        current_time = datetime.utcnow()
        
        # Rate limiting: max 5 attempts per minute
        attempts = self.rate_limiters[key]
        attempts.append(current_time)
        
        # Count attempts in the last minute
        minute_ago = current_time - timedelta(minutes=1)
        recent_attempts = [t for t in attempts if t > minute_ago]
        
        if len(recent_attempts) > 5:
            return True
        
        return False
    
    async def _detect_data_exfiltration(self, flow: NetworkFlow) -> bool:
        """Detect potential data exfiltration"""
        # Suspicious if large amounts of data are being sent out
        # This is a simplified heuristic
        
        # Flag if more than 100MB transferred in a single flow
        if flow.bytes_sent > 100 * 1024 * 1024:
            return True
        
        # Flag if high data rate to external IPs
        if (not self._is_internal_ip(flow.destination_ip) and 
            flow.duration_seconds > 0 and
            (flow.bytes_sent / flow.duration_seconds) > 10 * 1024 * 1024):  # 10MB/s
            return True
        
        return False
    
    def _is_internal_ip(self, ip: str) -> bool:
        """Check if IP is internal/private"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    async def _flow_analysis_loop(self):
        """Periodic analysis of accumulated flows"""
        while self.monitoring:
            try:
                await self._analyze_traffic_patterns()
                await asyncio.sleep(60)  # Analyze every minute
            
            except Exception as e:
                logger.error(f"Error in flow analysis: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_traffic_patterns(self):
        """Analyze traffic patterns for anomalies"""
        # Analyze flows for behavioral anomalies
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        # Get recent flows
        recent_flows = [
            flow for flow in self.flow_cache.values()
            if flow.start_time > hour_ago
        ]
        
        if not recent_flows:
            return
        
        # Detect traffic volume anomalies
        await self._detect_traffic_anomalies(recent_flows)
        
        # Detect unusual connection patterns
        await self._detect_connection_anomalies(recent_flows)
    
    async def _detect_traffic_anomalies(self, flows: List[NetworkFlow]):
        """Detect traffic volume anomalies"""
        # Calculate average traffic volumes
        total_bytes = sum(flow.bytes_sent + flow.bytes_received for flow in flows)
        avg_flow_size = total_bytes / len(flows) if flows else 0
        
        # Flag unusually large flows
        for flow in flows:
            flow_size = flow.bytes_sent + flow.bytes_received
            if flow_size > avg_flow_size * 10:  # 10x average
                logger.warning(f"Anomalous traffic volume detected: {flow_size} bytes in flow {flow.flow_id}")
    
    async def _detect_connection_anomalies(self, flows: List[NetworkFlow]):
        """Detect unusual connection patterns"""
        # Group flows by source IP
        ip_flows = defaultdict(list)
        for flow in flows:
            ip_flows[flow.source_ip].append(flow)
        
        # Detect IPs with unusually high connection counts
        for source_ip, ip_flow_list in ip_flows.items():
            if len(ip_flow_list) > 100:  # More than 100 connections per hour
                unique_destinations = len(set(flow.destination_ip for flow in ip_flow_list))
                if unique_destinations > 20:  # Connecting to many different hosts
                    logger.warning(f"Suspicious connection pattern from {source_ip}: {len(ip_flow_list)} connections to {unique_destinations} hosts")
    
    async def _cleanup_loop(self):
        """Clean up old data"""
        while self.monitoring:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)
                
                # Clean old flows
                old_flows = [
                    flow_id for flow_id, flow in self.flow_cache.items()
                    if flow.end_time < cutoff_time
                ]
                
                for flow_id in old_flows:
                    del self.flow_cache[flow_id]
                
                # Clean old connection tracking
                old_connections = [
                    ip for ip, tracking in self.connection_tracking.items()
                    if tracking['last_seen'] < cutoff_time
                ]
                
                for ip in old_connections:
                    del self.connection_tracking[ip]
                
                if old_flows or old_connections:
                    logger.info(f"Cleaned up {len(old_flows)} old flows and {len(old_connections)} old connections")
                
                await asyncio.sleep(3600)  # Cleanup every hour
            
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _create_security_event(self, event_type: str, severity: str,
                                   source_ip: str, destination_ip: str,
                                   source_port: Optional[int], destination_port: Optional[int],
                                   protocol: str, description: str, raw_data: str) -> SecurityEvent:
        """Create a security event"""
        return SecurityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            destination_ip=destination_ip,
            source_port=source_port,
            destination_port=destination_port,
            protocol=protocol,
            timestamp=datetime.utcnow(),
            description=description,
            raw_data=raw_data,
            threat_indicators=[source_ip],
            confidence_score=0.8,
            blocked=False,
            action_taken='logged'
        )

class HostBasedDetection:
    """Host-based intrusion detection"""
    
    def __init__(self):
        self.file_watchers = {}
        self.process_monitors = {}
        self.log_analyzers = {}
        self.baseline_established = False
        self.process_baseline = {}
        self.file_integrity_baseline = {}
    
    async def establish_baseline(self):
        """Establish baseline for normal system behavior"""
        logger.info("Establishing host-based detection baseline")
        
        # Baseline running processes
        await self._baseline_processes()
        
        # Baseline file integrity
        await self._baseline_file_integrity()
        
        self.baseline_established = True
        logger.info("Baseline established")
    
    async def _baseline_processes(self):
        """Create baseline of normal running processes"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name']
                    
                    if proc_name not in self.process_baseline:
                        self.process_baseline[proc_name] = {
                            'count': 0,
                            'avg_cpu': 0,
                            'avg_memory': 0,
                            'cmdlines': set()
                        }
                    
                    baseline = self.process_baseline[proc_name]
                    baseline['count'] += 1
                    baseline['avg_cpu'] += proc_info.get('cpu_percent', 0)
                    baseline['avg_memory'] += proc_info.get('memory_percent', 0)
                    
                    if proc_info.get('cmdline'):
                        baseline['cmdlines'].add(' '.join(proc_info['cmdline']))
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Calculate averages
            for proc_name, baseline in self.process_baseline.items():
                if baseline['count'] > 0:
                    baseline['avg_cpu'] /= baseline['count']
                    baseline['avg_memory'] /= baseline['count']
        
        except Exception as e:
            logger.error(f"Error establishing process baseline: {e}")
    
    async def _baseline_file_integrity(self):
        """Create baseline for critical file integrity"""
        critical_paths = [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/sudoers',
            '/etc/ssh/sshd_config',
            '/bin/bash',
            '/bin/sh',
            '/usr/bin/sudo'
        ]
        
        for path in critical_paths:
            try:
                hash_value = await self._calculate_file_hash(path)
                if hash_value:
                    self.file_integrity_baseline[path] = {
                        'hash': hash_value,
                        'last_checked': datetime.utcnow()
                    }
            except Exception as e:
                logger.warning(f"Could not baseline file {path}: {e}")
    
    async def _calculate_file_hash(self, filepath: str) -> Optional[str]:
        """Calculate SHA256 hash of file"""
        try:
            import hashlib
            
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(filepath, 'rb') as f:
                async for chunk in f:
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
        
        except Exception as e:
            logger.error(f"Error calculating hash for {filepath}: {e}")
            return None
    
    async def monitor_processes(self) -> List[SecurityEvent]:
        """Monitor for suspicious process activities"""
        events = []
        
        if not self.baseline_established:
            return events
        
        try:
            import psutil
            
            current_processes = {}
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name']
                    
                    if proc_name not in current_processes:
                        current_processes[proc_name] = []
                    
                    current_processes[proc_name].append(proc_info)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for anomalies
            for proc_name, proc_list in current_processes.items():
                if proc_name in self.process_baseline:
                    baseline = self.process_baseline[proc_name]
                    
                    # Check for unusual process count
                    if len(proc_list) > baseline['count'] * 3:  # 3x normal count
                        events.append(SecurityEvent(
                            event_id=str(uuid.uuid4()),
                            event_type='process_anomaly',
                            severity='medium',
                            source_ip='localhost',
                            destination_ip='localhost',
                            source_port=None,
                            destination_port=None,
                            protocol='host',
                            timestamp=datetime.utcnow(),
                            description=f"Unusual number of {proc_name} processes: {len(proc_list)} (normal: {baseline['count']})",
                            raw_data=json.dumps([p for p in proc_list]),
                            threat_indicators=[proc_name],
                            confidence_score=0.7,
                            blocked=False,
                            action_taken='logged'
                        ))
                    
                    # Check for unusual command lines
                    for proc_info in proc_list:
                        cmdline = ' '.join(proc_info.get('cmdline', []))
                        if cmdline and cmdline not in baseline['cmdlines']:
                            # New command line for known process
                            events.append(SecurityEvent(
                                event_id=str(uuid.uuid4()),
                                event_type='new_process_cmdline',
                                severity='low',
                                source_ip='localhost',
                                destination_ip='localhost',
                                source_port=None,
                                destination_port=None,
                                protocol='host',
                                timestamp=datetime.utcnow(),
                                description=f"New command line for {proc_name}: {cmdline}",
                                raw_data=json.dumps(proc_info),
                                threat_indicators=[proc_name, cmdline],
                                confidence_score=0.5,
                                blocked=False,
                                action_taken='logged'
                            ))
                
                else:
                    # Completely new process type
                    events.append(SecurityEvent(
                        event_id=str(uuid.uuid4()),
                        event_type='new_process',
                        severity='medium',
                        source_ip='localhost',
                        destination_ip='localhost',
                        source_port=None,
                        destination_port=None,
                        protocol='host',
                        timestamp=datetime.utcnow(),
                        description=f"New process type detected: {proc_name}",
                        raw_data=json.dumps(proc_list),
                        threat_indicators=[proc_name],
                        confidence_score=0.6,
                        blocked=False,
                        action_taken='logged'
                    ))
        
        except Exception as e:
            logger.error(f"Error monitoring processes: {e}")
        
        return events
    
    async def check_file_integrity(self) -> List[SecurityEvent]:
        """Check file integrity against baseline"""
        events = []
        
        for filepath, baseline in self.file_integrity_baseline.items():
            try:
                current_hash = await self._calculate_file_hash(filepath)
                
                if current_hash and current_hash != baseline['hash']:
                    events.append(SecurityEvent(
                        event_id=str(uuid.uuid4()),
                        event_type='file_integrity_violation',
                        severity='critical',
                        source_ip='localhost',
                        destination_ip='localhost',
                        source_port=None,
                        destination_port=None,
                        protocol='host',
                        timestamp=datetime.utcnow(),
                        description=f"File integrity violation: {filepath}",
                        raw_data=f"Expected: {baseline['hash']}, Current: {current_hash}",
                        threat_indicators=[filepath],
                        confidence_score=0.9,
                        blocked=False,
                        action_taken='logged'
                    ))
                    
                    # Update baseline with new hash (after logging the event)
                    baseline['hash'] = current_hash
                    baseline['last_checked'] = datetime.utcnow()
            
            except Exception as e:
                logger.error(f"Error checking integrity of {filepath}: {e}")
        
        return events

class LogAnalyzer:
    """Analyzes system logs for security events"""
    
    def __init__(self):
        self.log_patterns = {
            'failed_login': [
                r'Failed password for .* from (\d+\.\d+\.\d+\.\d+)',
                r'authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)'
            ],
            'privilege_escalation': [
                r'sudo:.*COMMAND=.*',
                r'su:.*session opened for user root'
            ],
            'service_failures': [
                r'systemd.*Failed to start',
                r'service.*failed'
            ]
        }
        self.monitored_logs = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/secure'
        ]
    
    async def analyze_logs(self, hours: int = 1) -> List[SecurityEvent]:
        """Analyze system logs for security events"""
        events = []
        
        for log_file in self.monitored_logs:
            try:
                log_events = await self._analyze_log_file(log_file, hours)
                events.extend(log_events)
            except Exception as e:
                logger.warning(f"Could not analyze log file {log_file}: {e}")
        
        return events
    
    async def _analyze_log_file(self, log_file: str, hours: int) -> List[SecurityEvent]:
        """Analyze a single log file"""
        events = []
        
        try:
            # Use journalctl for systemd logs or read files directly
            if log_file in ['/var/log/auth.log', '/var/log/secure']:
                # Read authentication logs
                events.extend(await self._analyze_auth_logs(log_file, hours))
            else:
                # Read other system logs
                events.extend(await self._analyze_system_logs(log_file, hours))
        
        except Exception as e:
            logger.error(f"Error analyzing log file {log_file}: {e}")
        
        return events
    
    async def _analyze_auth_logs(self, log_file: str, hours: int) -> List[SecurityEvent]:
        """Analyze authentication logs"""
        events = []
        
        try:
            # Use journalctl to get recent auth logs
            cmd = ['journalctl', '-u', 'ssh', '--since', f'{hours} hours ago', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                log_lines = result.stdout.split('\n')
                
                for line in log_lines:
                    # Check for failed login attempts
                    for pattern in self.log_patterns['failed_login']:
                        match = re.search(pattern, line)
                        if match:
                            source_ip = match.group(1)
                            
                            events.append(SecurityEvent(
                                event_id=str(uuid.uuid4()),
                                event_type='failed_login',
                                severity='medium',
                                source_ip=source_ip,
                                destination_ip='localhost',
                                source_port=None,
                                destination_port=22,
                                protocol='ssh',
                                timestamp=datetime.utcnow(),
                                description=f"Failed login attempt from {source_ip}",
                                raw_data=line,
                                threat_indicators=[source_ip],
                                confidence_score=0.8,
                                blocked=False,
                                action_taken='logged'
                            ))
                            break
                    
                    # Check for privilege escalation
                    for pattern in self.log_patterns['privilege_escalation']:
                        if re.search(pattern, line):
                            events.append(SecurityEvent(
                                event_id=str(uuid.uuid4()),
                                event_type='privilege_escalation',
                                severity='high',
                                source_ip='localhost',
                                destination_ip='localhost',
                                source_port=None,
                                destination_port=None,
                                protocol='host',
                                timestamp=datetime.utcnow(),
                                description="Privilege escalation detected",
                                raw_data=line,
                                threat_indicators=['sudo', 'su'],
                                confidence_score=0.7,
                                blocked=False,
                                action_taken='logged'
                            ))
                            break
        
        except Exception as e:
            logger.error(f"Error analyzing auth logs: {e}")
        
        return events
    
    async def _analyze_system_logs(self, log_file: str, hours: int) -> List[SecurityEvent]:
        """Analyze general system logs"""
        events = []
        
        try:
            # Get recent system logs
            cmd = ['journalctl', '--since', f'{hours} hours ago', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                log_lines = result.stdout.split('\n')
                
                for line in log_lines:
                    # Check for service failures
                    for pattern in self.log_patterns['service_failures']:
                        if re.search(pattern, line):
                            events.append(SecurityEvent(
                                event_id=str(uuid.uuid4()),
                                event_type='service_failure',
                                severity='medium',
                                source_ip='localhost',
                                destination_ip='localhost',
                                source_port=None,
                                destination_port=None,
                                protocol='host',
                                timestamp=datetime.utcnow(),
                                description="Service failure detected",
                                raw_data=line,
                                threat_indicators=['service_failure'],
                                confidence_score=0.6,
                                blocked=False,
                                action_taken='logged'
                            ))
                            break
        
        except Exception as e:
            logger.error(f"Error analyzing system logs: {e}")
        
        return events

class ResponseEngine:
    """Automated response to security events"""
    
    def __init__(self):
        self.response_rules = {
            'brute_force': ['block_ip', 'notify_admin'],
            'port_scan': ['block_ip', 'log_detail'],
            'file_integrity_violation': ['alert_critical', 'backup_file'],
            'privilege_escalation': ['alert_critical', 'lock_account']
        }
        self.blocked_ips = set()
        self.quarantined_files = set()
    
    async def respond_to_event(self, event: SecurityEvent) -> List[str]:
        """Execute automated response to security event"""
        actions_taken = []
        
        if event.event_type in self.response_rules:
            for action in self.response_rules[event.event_type]:
                try:
                    success = await self._execute_action(action, event)
                    if success:
                        actions_taken.append(action)
                except Exception as e:
                    logger.error(f"Failed to execute action {action}: {e}")
        
        return actions_taken
    
    async def _execute_action(self, action: str, event: SecurityEvent) -> bool:
        """Execute a specific response action"""
        if action == 'block_ip':
            return await self._block_ip(event.source_ip)
        elif action == 'notify_admin':
            return await self._notify_admin(event)
        elif action == 'log_detail':
            return await self._log_detailed_event(event)
        elif action == 'alert_critical':
            return await self._send_critical_alert(event)
        elif action == 'backup_file':
            return await self._backup_file(event)
        elif action == 'lock_account':
            return await self._lock_account(event)
        
        return False
    
    async def _block_ip(self, ip: str) -> bool:
        """Block IP address using iptables"""
        try:
            if ip in self.blocked_ips:
                return True  # Already blocked
            
            # Add iptables rule to block IP
            cmd = ['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.blocked_ips.add(ip)
                logger.info(f"Blocked IP address: {ip}")
                return True
            else:
                logger.error(f"Failed to block IP {ip}: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error blocking IP {ip}: {e}")
            return False
    
    async def _notify_admin(self, event: SecurityEvent) -> bool:
        """Send notification to administrator"""
        try:
            # This would integrate with notification systems
            logger.warning(f"ADMIN NOTIFICATION: {event.description}")
            
            # Could send email, Slack message, etc.
            notification_data = {
                'event_id': event.event_id,
                'type': event.event_type,
                'severity': event.severity,
                'description': event.description,
                'timestamp': event.timestamp.isoformat(),
                'source_ip': event.source_ip
            }
            
            # Save notification to file for external processing
            async with aiofiles.open('/var/log/ainflue/security_notifications.log', 'a') as f:
                await f.write(json.dumps(notification_data) + '\n')
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _log_detailed_event(self, event: SecurityEvent) -> bool:
        """Log detailed event information"""
        try:
            detailed_log = {
                'timestamp': event.timestamp.isoformat(),
                'event': asdict(event)
            }
            
            async with aiofiles.open('/var/log/ainflue/detailed_security_events.log', 'a') as f:
                await f.write(json.dumps(detailed_log) + '\n')
            
            return True
        
        except Exception as e:
            logger.error(f"Error logging detailed event: {e}")
            return False
    
    async def _send_critical_alert(self, event: SecurityEvent) -> bool:
        """Send critical security alert"""
        try:
            alert_data = {
                'CRITICAL_SECURITY_ALERT': True,
                'event_id': event.event_id,
                'type': event.event_type,
                'description': event.description,
                'timestamp': event.timestamp.isoformat(),
                'confidence': event.confidence_score,
                'threat_indicators': event.threat_indicators
            }
            
            # Log critical alert
            logger.critical(f"CRITICAL SECURITY ALERT: {event.description}")
            
            # Save to critical alerts file
            async with aiofiles.open('/var/log/ainflue/critical_security_alerts.log', 'a') as f:
                await f.write(json.dumps(alert_data) + '\n')
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending critical alert: {e}")
            return False
    
    async def _backup_file(self, event: SecurityEvent) -> bool:
        """Backup file mentioned in security event"""
        try:
            # Extract file path from threat indicators
            file_paths = [indicator for indicator in event.threat_indicators if indicator.startswith('/')]
            
            for file_path in file_paths:
                try:
                    backup_path = f"/var/backup/security/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file_path.replace('/', '_')}"
                    
                    # Create backup directory
                    import os
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    # Copy file
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    
                    logger.info(f"Backed up file {file_path} to {backup_path}")
                
                except Exception as e:
                    logger.error(f"Failed to backup file {file_path}: {e}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error in backup file action: {e}")
            return False
    
    async def _lock_account(self, event: SecurityEvent) -> bool:
        """Lock user account involved in security event"""
        try:
            # This is a placeholder - would integrate with actual account management
            logger.warning(f"ACCOUNT LOCK requested for security event: {event.event_id}")
            
            # In a real implementation, this would:
            # 1. Identify the user account from the event
            # 2. Lock the account in the authentication system
            # 3. Log the action
            
            return True
        
        except Exception as e:
            logger.error(f"Error locking account: {e}")
            return False

class IntrusionDetectionSystem:
    """Main Intrusion Detection System engine"""
    
    def __init__(self):
        self.network_monitor = NetworkMonitor()
        self.host_monitor = HostBasedDetection()
        self.log_analyzer = LogAnalyzer()
        self.response_engine = ResponseEngine()
        self.detection_enabled = False
        self.event_queue = deque(maxlen=10000)
        self.statistics = {
            'events_detected': 0,
            'events_blocked': 0,
            'false_positives': 0,
            'start_time': None
        }
    
    async def initialize(self):
        """Initialize the IDS"""
        logger.info("Initializing Ainflue Intrusion Detection System")
        
        # Establish baselines
        await self.host_monitor.establish_baseline()
        
        self.statistics['start_time'] = datetime.utcnow()
        logger.info("IDS initialization complete")
    
    async def start_detection(self):
        """Start intrusion detection"""
        self.detection_enabled = True
        logger.info("Starting intrusion detection")
        
        detection_tasks = [
            self._network_detection_loop(),
            self._host_detection_loop(),
            self._log_analysis_loop(),
            self._event_processing_loop()
        ]
        
        await asyncio.gather(*detection_tasks)
    
    def stop_detection(self):
        """Stop intrusion detection"""
        self.detection_enabled = False
        self.network_monitor.stop_monitoring()
        logger.info("Intrusion detection stopped")
    
    async def _network_detection_loop(self):
        """Network-based detection loop"""
        await self.network_monitor.start_network_monitoring()
    
    async def _host_detection_loop(self):
        """Host-based detection loop"""
        while self.detection_enabled:
            try:
                # Monitor processes
                process_events = await self.host_monitor.monitor_processes()
                for event in process_events:
                    await self._queue_event(event)
                
                # Check file integrity
                integrity_events = await self.host_monitor.check_file_integrity()
                for event in integrity_events:
                    await self._queue_event(event)
                
                await asyncio.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Error in host detection loop: {e}")
                await asyncio.sleep(60)
    
    async def _log_analysis_loop(self):
        """Log analysis loop"""
        while self.detection_enabled:
            try:
                log_events = await self.log_analyzer.analyze_logs(hours=1)
                for event in log_events:
                    await self._queue_event(event)
                
                await asyncio.sleep(300)  # Analyze logs every 5 minutes
            
            except Exception as e:
                logger.error(f"Error in log analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _queue_event(self, event: SecurityEvent):
        """Queue security event for processing"""
        self.event_queue.append(event)
        self.statistics['events_detected'] += 1
    
    async def _event_processing_loop(self):
        """Process queued security events"""
        while self.detection_enabled:
            try:
                if self.event_queue:
                    event = self.event_queue.popleft()
                    await self._process_event(event)
                else:
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: SecurityEvent):
        """Process a single security event"""
        try:
            # Log the event
            logger.info(f"Security event detected: {event.event_type} - {event.description}")
            
            # Execute automated response
            actions_taken = await self.response_engine.respond_to_event(event)
            
            if actions_taken:
                event.action_taken = ', '.join(actions_taken)
                if 'block_ip' in actions_taken:
                    event.blocked = True
                    self.statistics['events_blocked'] += 1
            
            # Store event for analysis
            await self._store_event(event)
            
        except Exception as e:
            logger.error(f"Error processing security event: {e}")
    
    async def _store_event(self, event: SecurityEvent):
        """Store security event for later analysis"""
        try:
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            
            async with aiofiles.open('/var/log/ainflue/security_events.log', 'a') as f:
                await f.write(json.dumps(event_data) + '\n')
        
        except Exception as e:
            logger.error(f"Error storing event: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get IDS statistics"""
        if self.statistics['start_time']:
            uptime = datetime.utcnow() - self.statistics['start_time']
            uptime_hours = uptime.total_seconds() / 3600
        else:
            uptime_hours = 0
        
        return {
            'detection_enabled': self.detection_enabled,
            'events_detected': self.statistics['events_detected'],
            'events_blocked': self.statistics['events_blocked'],
            'false_positives': self.statistics['false_positives'],
            'uptime_hours': uptime_hours,
            'events_per_hour': self.statistics['events_detected'] / max(uptime_hours, 1),
            'queue_size': len(self.event_queue),
            'blocked_ips_count': len(self.response_engine.blocked_ips)
        }
    
    async def get_recent_events(self, hours: int = 24, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent security events"""
        events = []
        
        try:
            # Read from event log file
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            async with aiofiles.open('/var/log/ainflue/security_events.log', 'r') as f:
                async for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        
                        if event_time > cutoff_time:
                            if not event_type or event_data['event_type'] == event_type:
                                events.append(event_data)
                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        
        except FileNotFoundError:
            pass  # No events file yet
        except Exception as e:
            logger.error(f"Error reading recent events: {e}")
        
        return sorted(events, key=lambda x: x['timestamp'], reverse=True)

async def main():
    """Main function for testing"""
    ids = IntrusionDetectionSystem()
    
    try:
        await ids.initialize()
        
        # Start detection (run for a short time for testing)
        detection_task = asyncio.create_task(ids.start_detection())
        
        # Wait a bit to collect some data
        await asyncio.sleep(30)
        
        # Get statistics
        stats = ids.get_statistics()
        print(f"IDS Statistics: {json.dumps(stats, indent=2)}")
        
        # Get recent events
        events = await ids.get_recent_events(hours=1)
        print(f"Recent events: {len(events)}")
        
        # Stop detection
        ids.stop_detection()
        
    except KeyboardInterrupt:
        ids.stop_detection()
        logger.info("IDS stopped by user")

if __name__ == "__main__":
    asyncio.run(main())