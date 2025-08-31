"""Log Aggregator for IA Influencer Agent Platform
===============================================

Industrial-grade log aggregation with AI-powered pattern recognition,
security event correlation, and business intelligence extraction for
content protection, revenue tracking, and platform operations.

Features:
- Real-time log streaming and processing
- AI-powered anomaly detection in log patterns
- Security event correlation and threat detection
- Business intelligence extraction from operational logs
- Content protection audit logging
- Revenue tracking transaction logging
- Multi-tenant log isolation and privacy
- Automated log rotation and archival

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""
import asyncio
import logging
import time
import json
import re
import hashlib
import statistics
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import aioredis
import aiofiles
from pathlib import Path
import gzip
import numpy as np

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Enhanced log levels with business context"""    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    BUSINESS = "business"
    AUDIT = "audit"


class LogSource(Enum):
    """Enhanced log sources for IA Influencer Agent Platform"""    APPLICATION = "application"
    SYSTEM = "system"
    SECURITY = "security"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    EXTERNAL = "external"
    AI_ENGINE = "ai_engine"
    CONTENT_PROTECTION = "content_protection"
    REVENUE_TRACKING = "revenue_tracking"
    USER_AUTHENTICATION = "user_authentication"
    FINGERPRINT_SERVICE = "fingerprint_service"
    COLLABORATION = "collaboration"
    NOTIFICATION = "notification"
    PLATFORM_INTEGRATION = "platform_integration"


class LogCategory(Enum):
    """Business-specific log categories"""    USER_ACTION = "user_action"
    CONTENT_UPLOAD = "content_upload"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    PROTECTION_ALERT = "protection_alert"
    REVENUE_CALCULATION = "revenue_calculation"
    COLLABORATION_REQUEST = "collaboration_request"
    SECURITY_EVENT = "security_event"
    SYSTEM_PERFORMANCE = "system_performance"
    API_ACCESS = "api_access"
    DATA_PROCESSING = "data_processing"


@dataclass
class LogEntry:
    """Enhanced structured log entry with business context"""    timestamp: datetime
    level: LogLevel
    source: LogSource
    category: LogCategory
    service: str
    message: str
    logger_name: str = ""
    thread_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_message: str = ""
    business_impact: str = "low"  # low, medium, high, critical
    privacy_level: str = "public"  # public, internal, confidential, restricted
    geographic_region: Optional[str] = None
    platform: Optional[str] = None  # spotify, youtube, tiktok, etc.


@dataclass
class LogPattern:
    """Enhanced log pattern with AI-powered detection"""    name: str
    pattern: str
    level: LogLevel
    category: LogCategory
    action: str = "alert"  # alert, suppress, enhance, correlate
    threshold: int = 1
    window: int = 300  # seconds
    enabled: bool = True
    business_impact: str = "medium"
    correlation_rules: List[str] = field(default_factory=list)
    ai_confidence_threshold: float = 0.8
    auto_resolution: bool = False


@dataclass
class LogAlert:
    """Enhanced log-based alert with correlation"""    pattern_name: str
    count: int
    window_start: datetime
    window_end: datetime
    sample_entries: List[LogEntry]
    severity: str = "medium"
    correlation_id: Optional[str] = None
    related_alerts: List[str] = field(default_factory=list)
    business_impact_score: float = 0.5
    root_cause_analysis: Optional[str] = None
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class SecurityEvent:
    """Security event extracted from logs"""    event_type: str
    severity: str
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "unknown"  # success, failure, blocked
    details: Dict[str, Any] = field(default_factory=dict)
    threat_level: str = "low"  # low, medium, high, critical
    indicators: List[str] = field(default_factory=list)


@dataclass
class BusinessInsight:
    """Business intelligence extracted from logs"""    insight_type: str
    category: LogCategory
    timestamp: datetime
    value: float
    unit: str
    dimensions: Dict[str, str] = field(default_factory=dict)
    trend: str = "stable"  # increasing, decreasing, stable
    confidence: float = 1.0
    business_context: str = ""


class AILogAnalyzer:
    """AI-powered log analysis and pattern recognition"""    
    def __init__(self):
        self.pattern_baselines: Dict[str, Dict[str, float]] = {}
        self.anomaly_thresholds: Dict[str, Tuple[float, float]] = {}
        self.correlation_patterns: Dict[str, List[str]] = {}
        
    def detect_anomalies(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect anomalies in log patterns using AI"""        anomalies = []
        
        # Group entries by service and level
        service_level_counts = defaultdict(lambda: defaultdict(int))
        for entry in entries:
            service_level_counts[entry.service][entry.level.value] += 1
        
        # Detect anomalies in error rates
        for service, level_counts in service_level_counts.items():
            total_logs = sum(level_counts.values())
            error_rate = (level_counts.get('error', 0) + level_counts.get('critical', 0)) / total_logs
            
            if error_rate > 0.1:  # More than 10% error rate
                anomalies.append({
                    "type": "high_error_rate",
                    "service": service,
                    "error_rate": error_rate,
                    "total_logs": total_logs,
                    "severity": "high" if error_rate > 0.2 else "medium",
                    "confidence": min(error_rate * 5, 1.0)
                })
        
        # Detect unusual log volume patterns
        hourly_volumes = defaultdict(int)
        for entry in entries:
            hour = entry.timestamp.hour
            hourly_volumes[hour] += 1
        
        if hourly_volumes:
            avg_volume = statistics.mean(hourly_volumes.values())
            std_volume = statistics.stdev(hourly_volumes.values()) if len(hourly_volumes) > 1 else 0
            
            for hour, volume in hourly_volumes.items():
                if std_volume > 0 and abs(volume - avg_volume) > (2 * std_volume):
                    anomalies.append({
                        "type": "volume_anomaly",
                        "hour": hour,
                        "volume": volume,
                        "average": avg_volume,
                        "deviation": abs(volume - avg_volume) / std_volume,
                        "severity": "medium",
                        "confidence": 0.8
                    })
        
        return anomalies
    
    def extract_business_insights(self, entries: List[LogEntry]) -> List[BusinessInsight]:
        """Extract business intelligence from log data"""        insights = []
        
        # Content protection insights
        protection_events = [e for e in entries if e.category == LogCategory.PROTECTION_ALERT]
        if protection_events:
            platforms = defaultdict(int)
            for event in protection_events:
                platform = event.metadata.get('platform', 'unknown')
                platforms[platform] += 1
            
            for platform, count in platforms.items():
                insights.append(BusinessInsight(
                    insight_type="protection_activity",
                    category=LogCategory.PROTECTION_ALERT,
                    timestamp=datetime.utcnow(),
                    value=count,
                    unit="alerts",
                    dimensions={"platform": platform},
                    confidence=0.9,
                    business_context=f"Content protection alerts detected on {platform}"
                ))
        
        # Revenue tracking insights
        revenue_events = [e for e in entries if e.category == LogCategory.REVENUE_CALCULATION]
        if revenue_events:
            revenue_calculations = len(revenue_events)
            insights.append(BusinessInsight(
                insight_type="revenue_processing",
                category=LogCategory.REVENUE_CALCULATION,
                timestamp=datetime.utcnow(),
                value=revenue_calculations,
                unit="calculations",
                dimensions={},
                confidence=1.0,
                business_context="Revenue calculation operations processed"
            ))
        
        # User activity insights
        user_events = [e for e in entries if e.category == LogCategory.USER_ACTION and e.user_id]
        if user_events:
            unique_users = len(set(e.user_id for e in user_events if e.user_id))
            insights.append(BusinessInsight(
                insight_type="user_activity",
                category=LogCategory.USER_ACTION,
                timestamp=datetime.utcnow(),
                value=unique_users,
                unit="users",
                dimensions={},
                confidence=0.95,
                business_context="Active users generating log events"
            ))
        
        # AI processing insights
        ai_events = [e for e in entries if e.source == LogSource.AI_ENGINE]
        if ai_events:
            processing_time_logs = [e for e in ai_events if 'processing_time' in e.metadata]
            if processing_time_logs:
                avg_processing_time = statistics.mean(
                    float(e.metadata['processing_time']) for e in processing_time_logs
                )
                insights.append(BusinessInsight(
                    insight_type="ai_performance",
                    category=LogCategory.DATA_PROCESSING,
                    timestamp=datetime.utcnow(),
                    value=avg_processing_time,
                    unit="seconds",
                    dimensions={"service": "ai_engine"},
                    confidence=0.9,
                    business_context="Average AI processing time"
                ))
        
        return insights
    
    def correlate_events(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Find correlations between different log events"""        correlations = []
        
        # Group events by correlation_id and request_id
        correlation_groups = defaultdict(list)
        for entry in entries:
            if entry.correlation_id:
                correlation_groups[entry.correlation_id].append(entry)
            elif entry.request_id:
                correlation_groups[entry.request_id].append(entry)
        
        # Analyze correlated events
        for correlation_id, correlated_entries in correlation_groups.items():
            if len(correlated_entries) > 1:
                # Check for error patterns in correlated events
                error_entries = [e for e in correlated_entries if e.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
                if error_entries:
                    services = list(set(e.service for e in correlated_entries))
                    correlations.append({
                        "type": "error_correlation",
                        "correlation_id": correlation_id,
                        "error_count": len(error_entries),
                        "total_events": len(correlated_entries),
                        "affected_services": services,
                        "timespan": (
                            max(e.timestamp for e in correlated_entries) - 
                            min(e.timestamp for e in correlated_entries)
                        ).total_seconds(),
                        "confidence": 0.8
                    })
        
        # Temporal correlations
        entries_by_minute = defaultdict(list)
        for entry in entries:
            minute_key = entry.timestamp.replace(second=0, microsecond=0)
            entries_by_minute[minute_key].append(entry)
        
        # Look for spikes in different types of events
        for minute, minute_entries in entries_by_minute.items():
            if len(minute_entries) > 50:  # High activity minute
                categories = defaultdict(int)
                for entry in minute_entries:
                    categories[entry.category.value] += 1
                
                if len(categories) > 3:  # Multiple categories active
                    correlations.append({
                        "type": "activity_spike",
                        "timestamp": minute,
                        "total_events": len(minute_entries),
                        "categories": dict(categories),
                        "confidence": 0.7
                    })
        
        return correlations


class SecurityEventProcessor:
    """Process security-related log events"""    
    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.ip_reputation_cache: Dict[str, str] = {}
        
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """Load threat detection patterns"""        return {
            "brute_force": [
                r"Failed login attempt.*user_id.*",
                r"Authentication failed.*attempts.*",
                r"Invalid credentials.*"
            ],
            "sql_injection": [
                r".*UNION.*SELECT.*",
                r".*OR.*1=1.*",
                r".*DROP.*TABLE.*"
            ],
            "api_abuse": [
                r"Rate limit exceeded.*",
                r"Too many requests.*",
                r"API quota exceeded.*"
            ],
            "privilege_escalation": [
                r"Unauthorized access attempt.*",
                r"Permission denied.*admin.*",
                r"Escalation attempt.*"
            ],
            "data_exfiltration": [
                r"Large data export.*",
                r"Bulk download.*",
                r"Unusual data access pattern.*"
            ]
        }
    
    def process_security_events(self, entries: List[LogEntry]) -> List[SecurityEvent]:
        """Process log entries to extract security events"""        security_events = []
        
        for entry in entries:
            if entry.level == LogLevel.SECURITY or entry.source == LogSource.SECURITY:
                event = self._extract_security_event(entry)
                if event:
                    security_events.append(event)
            
            # Check for threat patterns in other logs
            threat_type = self._detect_threat_pattern(entry.message)
            if threat_type:
                event = SecurityEvent(
                    event_type=threat_type,
                    severity=self._calculate_threat_severity(threat_type, entry),
                    timestamp=entry.timestamp,
                    source_ip=entry.metadata.get('source_ip'),
                    user_id=entry.user_id,
                    resource=entry.metadata.get('resource'),
                    action=entry.metadata.get('action'),
                    details=entry.metadata,
                    threat_level=self._assess_threat_level(threat_type),
                    indicators=[entry.message]
                )
                security_events.append(event)
        
        return security_events
    
    def _extract_security_event(self, entry: LogEntry) -> Optional[SecurityEvent]:
        """Extract security event from a log entry"""        if not entry.metadata:
            return None
            
        return SecurityEvent(
            event_type=entry.metadata.get('event_type', 'unknown'),
            severity=entry.metadata.get('severity', 'medium'),
            timestamp=entry.timestamp,
            source_ip=entry.metadata.get('source_ip'),
            user_id=entry.user_id,
            resource=entry.metadata.get('resource'),
            action=entry.metadata.get('action'),
            result=entry.metadata.get('result', 'unknown'),
            details=entry.metadata,
            threat_level=entry.metadata.get('threat_level', 'low')
        )
    
    def _detect_threat_pattern(self, message: str) -> Optional[str]:
        """Detect threat patterns in log messages"""        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return threat_type
        return None
    
    def _calculate_threat_severity(self, threat_type: str, entry: LogEntry) -> str:
        """Calculate threat severity based on type and context"""        severity_map = {
            "brute_force": "medium",
            "sql_injection": "high",
            "api_abuse": "medium",
            "privilege_escalation": "high",
            "data_exfiltration": "critical"
        }
        return severity_map.get(threat_type, "low")
    
    def _assess_threat_level(self, threat_type: str) -> str:
        """Assess overall threat level"""        threat_levels = {
            "brute_force": "medium",
            "sql_injection": "high",
            "api_abuse": "low",
            "privilege_escalation": "critical",
            "data_exfiltration": "critical"
        }
        return threat_levels.get(threat_type, "low")


class LogAggregator:
    """    Industrial-grade log aggregation system with AI-powered analytics,
    specialized for content protection, revenue tracking, and platform operations.
    """    
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        log_directories: List[str] = None,
        retention_days: int = 30,
        enable_ai_analysis: bool = True,
        enable_security_processing: bool = True,
        max_log_size_mb: int = 100
    ):
        self.redis_client = redis_client
        self.log_directories = log_directories or ["/var/log/ia-influencer/"]
        self.retention_days = retention_days
        self.enable_ai_analysis = enable_ai_analysis
        self.enable_security_processing = enable_security_processing
        self.max_log_size_mb = max_log_size_mb
        compression_age_hours: int = 24
    ):
        self.redis_client = redis_client
        self.log_directories = log_directories or ["/var/log", "/app/logs"]
        self.retention_days = retention_days
        self.compression_age_hours = compression_age_hours
        
        # Processing state
        self._aggregating = False
        self._aggregator_task: Optional[asyncio.Task] = None
        self._pattern_matcher_task: Optional[asyncio.Task] = None
        self._log_watchers: List[asyncio.Task] = []
        
        # Log storage
        self._log_buffer: deque = deque(maxlen=10000)
        self._log_index: Dict[str, List[LogEntry]] = defaultdict(list)
        
        # Pattern detection
        self._patterns: Dict[str, LogPattern] = {}
        self._pattern_states: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._alert_callbacks: List[Callable] = []
        
        # Log parsing
        self._log_parsers: Dict[str, Callable] = {}
        self._default_parser = self._parse_structured_log
        
        # Statistics
        self._stats = {
            "total_processed": 0,
            "errors_detected": 0,
            "patterns_matched": 0,
            "alerts_generated": 0
        }
        
        # Register default patterns
        self._register_default_patterns()
        
    def _register_default_patterns(self):
        """Register default log patterns"""        
        # Error patterns
        self.register_pattern(LogPattern(
            name="application_errors",
            pattern=r"(ERROR|CRITICAL|Exception|Traceback)",
            level=LogLevel.ERROR,
            action="alert",
            threshold=5,
            window=300
        ))
        
        self.register_pattern(LogPattern(
            name="authentication_failures",
            pattern=r"(authentication failed|login failed|invalid credentials)",
            level=LogLevel.WARNING,
            action="alert",
            threshold=10,
            window=600
        ))
        
        self.register_pattern(LogPattern(
            name="database_errors",
            pattern=r"(database.*error|connection.*failed|timeout.*database)",
            level=LogLevel.ERROR,
            action="alert",
            threshold=3,
            window=180
        ))
        
        self.register_pattern(LogPattern(
            name="high_response_time",
            pattern=r"response_time.*([5-9]\d{2,}|[1-9]\d{3,})",  # >500ms
            level=LogLevel.WARNING,
            action="alert",
            threshold=20,
            window=300
        ))
        
        self.register_pattern(LogPattern(
            name="security_events",
            pattern=r"(security|breach|unauthorized|suspicious|attack)",
            level=LogLevel.CRITICAL,
            action="alert",
            threshold=1,
            window=60
        ))
        
        # Business patterns
        self.register_pattern(LogPattern(
            name="content_protection_violations",
            pattern=r"(content.*violation|copyright.*infringement|fingerprint.*match)",
            level=LogLevel.INFO,
            action="alert",
            threshold=1,
            window=0
        ))
        
        self.register_pattern(LogPattern(
            name="revenue_anomalies",
            pattern=r"(revenue.*anomaly|payment.*failed|payout.*error)",
            level=LogLevel.WARNING,
            action="alert",
            threshold=1,
            window=300
        ))
        
    async def start_aggregation(self):
        """Start log aggregation"""        if self._aggregating:
            logger.warning("Log aggregation already running")
            return
            
        self._aggregating = True
        
        # Start main aggregation task
        self._aggregator_task = asyncio.create_task(self._aggregation_loop())
        
        # Start pattern matching task
        self._pattern_matcher_task = asyncio.create_task(self._pattern_matching_loop())
        
        # Start log file watchers
        for log_dir in self.log_directories:
            if Path(log_dir).exists():
                watcher_task = asyncio.create_task(self._watch_log_directory(log_dir))
                self._log_watchers.append(watcher_task)
                
        logger.info("Log aggregation started")
        
    async def stop_aggregation(self):
        """Stop log aggregation"""        self._aggregating = False
        
        # Stop main tasks
        if self._aggregator_task:
            self._aggregator_task.cancel()
            try:
                await self._aggregator_task
            except asyncio.CancelledError:
                pass
                
        if self._pattern_matcher_task:
            self._pattern_matcher_task.cancel()
            try:
                await self._pattern_matcher_task
            except asyncio.CancelledError:
                pass
                
        # Stop log watchers
        for watcher in self._log_watchers:
            watcher.cancel()
            try:
                await watcher
            except asyncio.CancelledError:
                pass
                
        # Final processing
        await self._process_log_buffer()
        
        logger.info("Log aggregation stopped")
        
    async def _aggregation_loop(self):
        """Main aggregation loop"""        while self._aggregating:
            try:
                await self._process_log_buffer()
                await self._compress_old_logs()
                await self._cleanup_old_logs()
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in log aggregation loop: {e}")
                await asyncio.sleep(5)
                
    async def _pattern_matching_loop(self):
        """Pattern matching loop"""        while self._aggregating:
            try:
                await self._process_pattern_matching()
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pattern matching loop: {e}")
                await asyncio.sleep(5)
                
    async def _watch_log_directory(self, directory: str):
        """Watch log directory for new entries"""        log_dir = Path(directory)
        
        # This is a simplified implementation
        # In production, use libraries like watchdog for file system monitoring
        watched_files = {}
        
        while self._aggregating:
            try:
                for log_file in log_dir.glob("*.log"):
                    if log_file.is_file():
                        mtime = log_file.stat().st_mtime
                        
                        if str(log_file) not in watched_files:
                            watched_files[str(log_file)] = mtime
                            # Process entire file for new files
                            await self._process_log_file(log_file)
                        elif watched_files[str(log_file)] < mtime:
                            watched_files[str(log_file)] = mtime
                            # Process only new lines for modified files
                            await self._process_log_file_incremental(log_file)
                            
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error watching log directory {directory}: {e}")
                await asyncio.sleep(10)
                
    async def _process_log_file(self, log_file: Path):
        """Process entire log file"""        try:
            async with aiofiles.open(log_file, 'r') as f:
                async for line in f:
                    line = line.strip()
                    if line:
                        await self._process_log_line(line, str(log_file))
                        
        except Exception as e:
            logger.error(f"Error processing log file {log_file}: {e}")
            
    async def _process_log_file_incremental(self, log_file: Path):
        """Process new lines in modified log file"""        # This is a simplified implementation
        # In production, maintain file positions for each watched file
        await self._process_log_file(log_file)
        
    async def _process_log_line(self, line: str, source_file: str):
        """Process a single log line"""        try:
            # Determine parser based on file or content
            parser = self._get_parser_for_source(source_file)
            
            # Parse log entry
            log_entry = parser(line, source_file)
            if log_entry:
                # Add to buffer
                self._log_buffer.append(log_entry)
                
                # Update index
                self._update_log_index(log_entry)
                
                # Update statistics
                self._stats["total_processed"] += 1
                if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                    self._stats["errors_detected"] += 1
                    
        except Exception as e:
            logger.error(f"Error processing log line: {e}")
            
    def _get_parser_for_source(self, source_file: str) -> Callable:
        """Get appropriate parser for log source"""        file_name = Path(source_file).name
        
        # Check registered parsers
        for pattern, parser in self._log_parsers.items():
            if re.search(pattern, file_name):
                return parser
                
        return self._default_parser
        
    def _parse_structured_log(self, line: str, source_file: str) -> Optional[LogEntry]:
        """Parse structured log entry"""        try:
            # Try to parse as JSON first
            if line.startswith('{'):
                data = json.loads(line)
                return LogEntry(
                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
                    level=LogLevel(data.get('level', 'info').lower()),
                    source=LogSource(data.get('source', 'application').lower()),
                    service=data.get('service', 'unknown'),
                    message=data.get('message', ''),
                    logger_name=data.get('logger', ''),
                    thread_id=data.get('thread_id'),
                    request_id=data.get('request_id'),
                    user_id=data.get('user_id'),
                    session_id=data.get('session_id'),
                    tags=data.get('tags', []),
                    metadata=data.get('metadata', {}),
                    raw_message=line
                )
                
            # Parse common log format
            patterns = [
                # Standard format: timestamp level service message
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,\.]\d{3})\s+(\w+)\s+(\S+)\s+(.+)',
                # Syslog format
                r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+):\s*(.+)',
                # Simple format: level message
                r'(\w+):\s*(.+)'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 4:
                        timestamp_str, level_str, service, message = groups
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace(',', '.'))
                        except:
                            timestamp = datetime.utcnow()
                    elif len(groups) == 2:
                        level_str, message = groups
                        timestamp = datetime.utcnow()
                        service = Path(source_file).stem
                    else:
                        continue
                        
                    return LogEntry(
                        timestamp=timestamp,
                        level=self._parse_log_level(level_str),
                        source=self._detect_log_source(source_file, message),
                        service=service,
                        message=message,
                        raw_message=line
                    )
                    
        except Exception as e:
            logger.debug(f"Error parsing log line: {e}")
            
        # Fallback: create basic log entry
        return LogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO,
            source=LogSource.APPLICATION,
            service=Path(source_file).stem,
            message=line,
            raw_message=line
        )
        
    def _parse_log_level(self, level_str: str) -> LogLevel:
        """Parse log level string"""        level_map = {
            'debug': LogLevel.DEBUG,
            'info': LogLevel.INFO,
            'warn': LogLevel.WARNING,
            'warning': LogLevel.WARNING,
            'error': LogLevel.ERROR,
            'err': LogLevel.ERROR,
            'critical': LogLevel.CRITICAL,
            'crit': LogLevel.CRITICAL,
            'fatal': LogLevel.CRITICAL
        }
        
        return level_map.get(level_str.lower(), LogLevel.INFO)
        
    def _detect_log_source(self, source_file: str, message: str) -> LogSource:
        """Detect log source from file and content"""        file_name = Path(source_file).name.lower()
        message_lower = message.lower()
        
        if 'security' in file_name or any(word in message_lower for word in ['security', 'auth', 'login']):
            return LogSource.SECURITY
        elif 'system' in file_name or 'syslog' in file_name:
            return LogSource.SYSTEM
        elif any(word in message_lower for word in ['revenue', 'payment', 'business', 'user']):
            return LogSource.BUSINESS
        elif any(word in message_lower for word in ['performance', 'response_time', 'memory', 'cpu']):
            return LogSource.PERFORMANCE
        elif any(word in message_lower for word in ['external', 'api', 'webhook']):
            return LogSource.EXTERNAL
        else:
            return LogSource.APPLICATION
            
    def _update_log_index(self, log_entry: LogEntry):
        """Update log index for fast searching"""        # Index by time buckets (5-minute intervals)
        time_bucket = log_entry.timestamp.replace(second=0, microsecond=0)
        time_bucket = time_bucket.replace(minute=(time_bucket.minute // 5) * 5)
        bucket_key = time_bucket.isoformat()
        
        self._log_index[bucket_key].append(log_entry)
        
        # Limit index size
        if len(self._log_index[bucket_key]) > 1000:
            self._log_index[bucket_key] = self._log_index[bucket_key][-500:]
            
    async def _process_log_buffer(self):
        """Process log buffer"""        if not self._log_buffer:
            return
            
        # Store logs in Redis
        if self.redis_client:
            await self._store_logs_to_redis()
            
        # Clear processed logs from buffer
        # Keep some for pattern matching
        if len(self._log_buffer) > 5000:
            # Remove older entries
            for _ in range(len(self._log_buffer) - 2500):
                self._log_buffer.popleft()
                
    async def _store_logs_to_redis(self):
        """Store logs to Redis"""        try:
            pipeline = self.redis_client.pipeline()
            
            # Store recent logs
            for log_entry in list(self._log_buffer):
                key = f"logs:{log_entry.source.value}:{log_entry.service}"
                value = {
                    "timestamp": log_entry.timestamp.isoformat(),
                    "level": log_entry.level.value,
                    "message": log_entry.message,
                    "logger_name": log_entry.logger_name,
                    "request_id": log_entry.request_id,
                    "user_id": log_entry.user_id,
                    "tags": log_entry.tags,
                    "metadata": log_entry.metadata
                }
                
                # Store in time series
                pipeline.zadd(key, {json.dumps(value): log_entry.timestamp.timestamp()})
                
                # Cleanup old entries (keep 7 days)
                cutoff = time.time() - (7 * 24 * 3600)
                pipeline.zremrangebyscore(key, 0, cutoff)
                
            # Store aggregated statistics
            pipeline.hmset("logs:stats", self._stats)
            
            await pipeline.execute()
            
        except Exception as e:
            logger.error(f"Error storing logs to Redis: {e}")
            
    async def _process_pattern_matching(self):
        """Process pattern matching on recent logs"""        for pattern_name, pattern in self._patterns.items():
            if not pattern.enabled:
                continue
                
            try:
                await self._check_pattern_matches(pattern)
            except Exception as e:
                logger.error(f"Error checking pattern {pattern_name}: {e}")
                
    async def _check_pattern_matches(self, pattern: LogPattern):
        """Check for pattern matches in recent logs"""        now = datetime.utcnow()
        window_start = now - timedelta(seconds=pattern.window) if pattern.window > 0 else now
        
        matches = []
        
        # Search through recent logs
        for log_entry in list(self._log_buffer):
            if log_entry.timestamp < window_start:
                continue
                
            if log_entry.level == pattern.level or pattern.level == LogLevel.DEBUG:
                if re.search(pattern.pattern, log_entry.message, re.IGNORECASE):
                    matches.append(log_entry)
                    
        # Check if threshold exceeded
        if len(matches) >= pattern.threshold:
            await self._handle_pattern_match(pattern, matches, window_start, now)
            
    async def _handle_pattern_match(
        self,
        pattern: LogPattern,
        matches: List[LogEntry],
        window_start: datetime,
        window_end: datetime
    ):
        """Handle pattern match"""        self._stats["patterns_matched"] += 1
        
        if pattern.action == "alert":
            alert = LogAlert(
                pattern_name=pattern.name,
                count=len(matches),
                window_start=window_start,
                window_end=window_end,
                sample_entries=matches[:5],  # Include sample entries
                severity=self._determine_alert_severity(pattern, len(matches))
            )
            
            await self._fire_log_alert(alert)
            
        elif pattern.action == "suppress":
            # Suppress similar logs for a period
            pass
            
        elif pattern.action == "enhance":
            # Enhance log entries with additional context
            pass
            
    def _determine_alert_severity(self, pattern: LogPattern, match_count: int) -> str:
        """Determine alert severity based on pattern and count"""        if pattern.level == LogLevel.CRITICAL:
            return "critical"
        elif pattern.level == LogLevel.ERROR:
            return "high"
        elif match_count > pattern.threshold * 3:
            return "high"
        elif match_count > pattern.threshold * 2:
            return "medium"
        else:
            return "low"
            
    async def _fire_log_alert(self, alert: LogAlert):
        """Fire log alert"""        self._stats["alerts_generated"] += 1
        
        logger.warning(f"Log alert: {alert.pattern_name} - {alert.count} matches")
        
        # Store alert in Redis
        if self.redis_client:
            try:
                alert_data = {
                    "pattern_name": alert.pattern_name,
                    "count": alert.count,
                    "window_start": alert.window_start.isoformat(),
                    "window_end": alert.window_end.isoformat(),
                    "severity": alert.severity,
                    "sample_messages": [entry.message for entry in alert.sample_entries[:3]]
                }
                
                await self.redis_client.lpush(
                    "log_alerts",
                    json.dumps(alert_data)
                )
                
                # Keep only recent alerts
                await self.redis_client.ltrim("log_alerts", 0, 999)
                
            except Exception as e:
                logger.error(f"Error storing log alert: {e}")
                
        # Call alert callbacks
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
                
    async def _compress_old_logs(self):
        """Compress old log files"""        cutoff = datetime.utcnow() - timedelta(hours=self.compression_age_hours)
        
        for log_dir in self.log_directories:
            log_path = Path(log_dir)
            if not log_path.exists():
                continue
                
            for log_file in log_path.glob("*.log"):
                try:
                    if log_file.stat().st_mtime < cutoff.timestamp():
                        compressed_file = log_file.with_suffix('.log.gz')
                        
                        if not compressed_file.exists():
                            # Compress the file
                            with open(log_file, 'rb') as f_in:
                                with gzip.open(compressed_file, 'wb') as f_out:
                                    f_out.writelines(f_in)
                                    
                            log_file.unlink()  # Remove original
                            logger.info(f"Compressed log file: {log_file}")
                            
                except Exception as e:
                    logger.error(f"Error compressing log file {log_file}: {e}")
                    
    async def _cleanup_old_logs(self):
        """Clean up old compressed logs"""        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        
        for log_dir in self.log_directories:
            log_path = Path(log_dir)
            if not log_path.exists():
                continue
                
            for log_file in log_path.glob("*.log.gz"):
                try:
                    if log_file.stat().st_mtime < cutoff.timestamp():
                        log_file.unlink()
                        logger.info(f"Deleted old log file: {log_file}")
                        
                except Exception as e:
                    logger.error(f"Error deleting old log file {log_file}: {e}")
                    
    # Public interface methods
    def register_pattern(self, pattern: LogPattern):
        """Register a log pattern"""        self._patterns[pattern.name] = pattern
        logger.info(f"Registered log pattern: {pattern.name}")
        
    def register_parser(self, file_pattern: str, parser: Callable):
        """Register a custom log parser"""        self._log_parsers[file_pattern] = parser
        logger.info(f"Registered log parser for pattern: {file_pattern}")
        
    def register_alert_callback(self, callback: Callable):
        """Register alert callback"""        self._alert_callbacks.append(callback)
        logger.info("Registered log alert callback")
        
    async def search_logs(
        self,
        query: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        source: Optional[LogSource] = None,
        service: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search logs with filters"""        if not self.redis_client:
            return []
            
        try:
            # Get logs from Redis
            keys = await self.redis_client.keys("logs:*")
            all_logs = []
            
            for key in keys:
                # Apply service filter
                if service and service not in key.decode():
                    continue
                    
                # Get logs from time series
                start_score = start_time.timestamp() if start_time else 0
                end_score = end_time.timestamp() if end_time else time.time()
                
                logs = await self.redis_client.zrangebyscore(
                    key, start_score, end_score, withscores=True
                )
                
                for log_json, timestamp in logs:
                    log_data = json.loads(log_json)
                    log_data['timestamp'] = datetime.fromtimestamp(timestamp)
                    
                    # Apply filters
                    if level and log_data.get('level') != level.value:
                        continue
                        
                    if source and source.value not in key.decode():
                        continue
                        
                    # Apply text search
                    if query and query.lower() not in log_data.get('message', '').lower():
                        continue
                        
                    all_logs.append(log_data)
                    
            # Sort by timestamp and limit
            all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
            return all_logs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []
            
    async def get_log_summary(self) -> Dict[str, Any]:
        """Get log summary statistics"""        return {
            "total_processed": self._stats["total_processed"],
            "errors_detected": self._stats["errors_detected"],
            "patterns_matched": self._stats["patterns_matched"],
            "alerts_generated": self._stats["alerts_generated"],
            "buffer_size": len(self._log_buffer),
            "patterns_registered": len(self._patterns),
            "parsers_registered": len(self._log_parsers),
            "aggregation_active": self._aggregating
        }
        
    async def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent log alerts"""        if not self.redis_client:
            return []
            
        try:
            alerts = await self.redis_client.lrange("log_alerts", 0, limit - 1)
            return [json.loads(alert) for alert in alerts]
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []
