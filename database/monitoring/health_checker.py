"""
Database Health Checker

Comprehensive database health monitoring system with automated diagnostics,
health scoring, and proactive issue detection capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

  AVERTISSEMENT STRICT 
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import json
import statistics
import psutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, DatabaseError

from ..core.database import get_database_session
from ..models.monitoring import HealthCheckResult, DatabaseHealthStatus
from ...core.config import Settings
from ...utils.cache import RedisCache


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


class CheckCategory(Enum):
    """Health check categories"""
    CONNECTIVITY = "connectivity"
    PERFORMANCE = "performance"
    RESOURCES = "resources"
    REPLICATION = "replication"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    DATA_INTEGRITY = "data_integrity"
    CONFIGURATION = "configuration"


@dataclass
class HealthCheck:
    """Individual health check definition"""
    check_id: str
    name: str
    description: str
    category: CheckCategory
    sql_query: Optional[str]
    check_function: Optional[str]
    warning_threshold: Optional[float]
    critical_threshold: Optional[float]
    enabled: bool = True
    timeout_seconds: int = 30
    frequency_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        return data


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    check_id: str
    status: HealthStatus
    value: Optional[float]
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    execution_time_ms: float
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class HealthReport:
    """Comprehensive health report"""
    overall_status: HealthStatus
    health_score: float
    timestamp: datetime
    check_results: List[HealthCheckResult]
    summary_by_category: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['overall_status'] = self.overall_status.value
        data['timestamp'] = self.timestamp.isoformat()
        data['check_results'] = [result.to_dict() for result in self.check_results]
        return data


class DatabaseHealthChecker:
    """
    Comprehensive database health monitoring system.
    
    Features:
    - Multi-dimensional health checks
    - Automated issue detection
    - Health scoring algorithm
    - Proactive recommendations
    - Historical trend analysis
    - Customizable check definitions
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        
        # Health checking state
        self.checking_active = False
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results_history: List[HealthReport] = []
        self.last_health_report: Optional[HealthReport] = None
        
        # Initialize standard health checks
        self._initialize_standard_checks()
        
        self.logger.info("Database Health Checker initialized")
    
    def _initialize_standard_checks(self) -> None:
        """Initialize standard health checks"""
        
        # Connectivity checks
        self.add_health_check(HealthCheck(
            check_id="database_connectivity",
            name="Database Connectivity",
            description="Check if database is accessible and responding",
            category=CheckCategory.CONNECTIVITY,
            sql_query="SELECT 1",
            check_function=None,
            warning_threshold=None,
            critical_threshold=None,
            frequency_seconds=60
        ))
        
        # Performance checks
        self.add_health_check(HealthCheck(
            check_id="query_response_time",
            name="Query Response Time",
            description="Average query response time",
            category=CheckCategory.PERFORMANCE,
            sql_query="""
                SELECT avg(mean_exec_time) 
                FROM pg_stat_statements 
                WHERE calls > 100
            """,
            check_function=None,
            warning_threshold=500.0,  # 500ms
            critical_threshold=2000.0,  # 2s
            frequency_seconds=300
        ))
        
        self.add_health_check(HealthCheck(
            check_id="cache_hit_ratio",
            name="Cache Hit Ratio",
            description="Database buffer cache hit ratio",
            category=CheckCategory.PERFORMANCE,
            sql_query="""
                SELECT CASE 
                    WHEN sum(heap_blks_hit + heap_blks_read) = 0 THEN 1.0
                    ELSE sum(heap_blks_hit)::float / sum(heap_blks_hit + heap_blks_read)
                END * 100
                FROM pg_statio_user_tables
            """,
            check_function=None,
            warning_threshold=85.0,  # 85%
            critical_threshold=70.0,  # 70%
            frequency_seconds=300
        ))
        
        self.add_health_check(HealthCheck(
            check_id="active_connections",
            name="Active Connections",
            description="Number of active database connections",
            category=CheckCategory.RESOURCES,
            sql_query="""
                SELECT count(*)::float / 
                       (SELECT setting::float FROM pg_settings WHERE name = 'max_connections') * 100
                FROM pg_stat_activity 
                WHERE state = 'active'
            """,
            check_function=None,
            warning_threshold=70.0,  # 70%
            critical_threshold=90.0,  # 90%
            frequency_seconds=120
        ))
        
        # Resource checks
        self.add_health_check(HealthCheck(
            check_id="disk_usage",
            name="Disk Usage",
            description="Database disk space utilization",
            category=CheckCategory.RESOURCES,
            sql_query=None,
            check_function="check_disk_usage",
            warning_threshold=80.0,  # 80%
            critical_threshold=95.0,  # 95%
            frequency_seconds=600
        ))
        
        self.add_health_check(HealthCheck(
            check_id="memory_usage",
            name="Memory Usage",
            description="System memory utilization",
            category=CheckCategory.RESOURCES,
            sql_query=None,
            check_function="check_memory_usage",
            warning_threshold=85.0,  # 85%
            critical_threshold=95.0,  # 95%
            frequency_seconds=180
        ))
        
        # Lock and blocking checks
        self.add_health_check(HealthCheck(
            check_id="lock_waits",
            name="Lock Waits",
            description="Number of processes waiting for locks",
            category=CheckCategory.PERFORMANCE,
            sql_query="""
                SELECT count(*)
                FROM pg_stat_activity 
                WHERE wait_event_type = 'Lock'
            """,
            check_function=None,
            warning_threshold=5.0,
            critical_threshold=20.0,
            frequency_seconds=120
        ))
        
        self.add_health_check(HealthCheck(
            check_id="long_running_queries",
            name="Long Running Queries",
            description="Number of queries running longer than 5 minutes",
            category=CheckCategory.PERFORMANCE,
            sql_query="""
                SELECT count(*)
                FROM pg_stat_activity 
                WHERE state = 'active'
                AND query_start < now() - interval '5 minutes'
                AND query NOT LIKE '%pg_stat_activity%'
            """,
            check_function=None,
            warning_threshold=3.0,
            critical_threshold=10.0,
            frequency_seconds=180
        ))
        
        # Data integrity checks
        self.add_health_check(HealthCheck(
            check_id="replication_lag",
            name="Replication Lag",
            description="Replication lag in seconds",
            category=CheckCategory.REPLICATION,
            sql_query="""
                SELECT CASE 
                    WHEN pg_is_in_recovery() THEN 
                        EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                    ELSE 0
                END
            """,
            check_function=None,
            warning_threshold=30.0,  # 30 seconds
            critical_threshold=300.0,  # 5 minutes
            frequency_seconds=300
        ))
        
        # Maintenance checks
        self.add_health_check(HealthCheck(
            check_id="bloat_ratio",
            name="Table Bloat Ratio",
            description="Average table bloat ratio",
            category=CheckCategory.MAINTENANCE,
            sql_query="""
                SELECT COALESCE(AVG(
                    CASE WHEN relpages > 0 THEN 
                        (relpages - otta)::float / relpages * 100
                    ELSE 0 END
                ), 0)
                FROM (
                    SELECT schemaname, tablename, relpages, otta
                    FROM (
                        SELECT schemaname, tablename, relpages,
                               CEIL((cc.reltuples * (datahdr + ma - (CASE WHEN datahdr % ma = 0 THEN ma ELSE datahdr % ma END))) / (bs - 20::float)) AS otta
                        FROM (
                            SELECT schemaname, tablename, (datawidth + (hdr + ma - (CASE WHEN hdr % ma = 0 THEN ma ELSE hdr % ma END)))::numeric AS datahdr,
                                   (hdr + ma - (CASE WHEN hdr % ma = 0 THEN ma ELSE hdr % ma END)) AS ma, bs, relpages, reltuples
                            FROM (
                                SELECT schemaname, tablename, hdr, ma, bs, relpages, reltuples,
                                       SUM((1 - null_frac) * avg_width) AS datawidth
                                FROM pg_stats s2
                                JOIN (
                                    SELECT schemaname, tablename, 
                                           (SELECT current_setting('block_size')::numeric) AS bs,
                                           CASE WHEN relpages > 0 THEN relpages ELSE 0 END AS relpages,
                                           CASE WHEN reltuples > 0 THEN reltuples ELSE 0 END AS reltuples,
                                           23 AS hdr, 4 AS ma
                                    FROM pg_class c
                                    JOIN pg_namespace n ON n.oid = c.relnamespace
                                    WHERE relkind = 'r'
                                    AND n.nspname NOT IN ('information_schema', 'pg_catalog')
                                ) s1 USING (schemaname, tablename)
                                GROUP BY schemaname, tablename, hdr, ma, bs, relpages, reltuples
                            ) s3
                        ) s4
                        JOIN pg_class cc ON cc.relname = tablename
                        JOIN pg_namespace nn ON nn.oid = cc.relnamespace AND nn.nspname = schemaname
                    ) s5
                ) s6
                WHERE otta > 0
            """,
            check_function=None,
            warning_threshold=25.0,  # 25%
            critical_threshold=50.0,  # 50%
            frequency_seconds=3600
        ))
        
        # Configuration checks
        self.add_health_check(HealthCheck(
            check_id="checkpoint_frequency",
            name="Checkpoint Frequency",
            description="Time since last checkpoint",
            category=CheckCategory.CONFIGURATION,
            sql_query="""
                SELECT EXTRACT(EPOCH FROM (now() - stats_reset))
                FROM pg_stat_bgwriter
            """,
            check_function=None,
            warning_threshold=1800.0,  # 30 minutes
            critical_threshold=3600.0,  # 1 hour
            frequency_seconds=600
        ))
    
    def add_health_check(self, check: HealthCheck) -> None:
        """Add health check definition"""
        self.health_checks[check.check_id] = check
        self.logger.debug(f"Added health check: {check.name}")
    
    def remove_health_check(self, check_id: str) -> bool:
        """Remove health check"""
        if check_id in self.health_checks:
            del self.health_checks[check_id]
            self.logger.debug(f"Removed health check: {check_id}")
            return True
        return False
    
    async def start_health_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self.checking_active:
            self.logger.warning("Health monitoring already active")
            return
        
        self.checking_active = True
        self.logger.info("Starting database health monitoring")
        
        try:
            # Start monitoring tasks for each check
            tasks = []
            for check_id, check in self.health_checks.items():
                if check.enabled:
                    task = asyncio.create_task(
                        self._health_check_loop(check_id, check)
                    )
                    tasks.append(task)
            
            # Start report generation task
            report_task = asyncio.create_task(self._generate_health_reports())
            tasks.append(report_task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Health monitoring error: {e}")
            self.checking_active = False
            raise
    
    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring"""
        self.checking_active = False
        self.logger.info("Health monitoring stopped")
    
    async def _health_check_loop(self, check_id: str, check: HealthCheck) -> None:
        """Continuous loop for individual health check"""
        while self.checking_active:
            try:
                result = await self._execute_health_check(check)
                if result:
                    await self._store_check_result(check_id, result)
                
                await asyncio.sleep(check.frequency_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in health check {check_id}: {e}")
                await asyncio.sleep(check.frequency_seconds)
    
    async def _execute_health_check(self, check: HealthCheck) -> Optional[HealthCheckResult]:
        """Execute individual health check"""
        start_time = time.time()
        
        try:
            # Execute based on check type
            if check.sql_query:
                value, error = await self._execute_sql_check(check)
            elif check.check_function:
                value, error = await self._execute_function_check(check)
            else:
                return None
            
            execution_time = (time.time() - start_time) * 1000
            
            # Determine status based on thresholds
            status = self._determine_check_status(check, value, error)
            
            # Generate message
            message = self._generate_check_message(check, status, value, error)
            
            result = HealthCheckResult(
                check_id=check.check_id,
                status=status,
                value=value,
                message=message,
                details={
                    "check_name": check.name,
                    "category": check.category.value,
                    "thresholds": {
                        "warning": check.warning_threshold,
                        "critical": check.critical_threshold
                    }
                },
                timestamp=datetime.utcnow(),
                execution_time_ms=execution_time,
                error=error
            )
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_id=check.check_id,
                status=HealthStatus.CRITICAL,
                value=None,
                message=f"Health check execution failed: {str(e)}",
                details={"check_name": check.name, "category": check.category.value},
                timestamp=datetime.utcnow(),
                execution_time_ms=execution_time,
                error=str(e)
            )
    
    async def _execute_sql_check(self, check: HealthCheck) -> Tuple[Optional[float], Optional[str]]:
        """Execute SQL-based health check"""



        try:
            async with get_database_session() as session:
                # Set query timeout
                await session.execute(text(f"SET statement_timeout = '{check.timeout_seconds}s'"))
                
                result = await session.execute(text(check.sql_query))
                value = result.scalar()
                
                if value is not None:
                    return float(value), None
                else:
                    return None, "Query returned NULL"
                    
        except (OperationalError, DatabaseError) as e:
            return None, f"Database error: {str(e)}"
        except Exception as e:
            return None, f"Execution error: {str(e)}"
    
    async def _execute_function_check(self, check: HealthCheck) -> Tuple[Optional[float], Optional[str]]:
        """Execute function-based health check"""



        try:
            if check.check_function == "check_disk_usage":
                return await self._check_disk_usage()
            elif check.check_function == "check_memory_usage":
                return await self._check_memory_usage()
            else:
                return None, f"Unknown check function: {check.check_function}"
                
        except Exception as e:
            return None, f"Function execution error: {str(e)}"
    
    async def _check_disk_usage(self) -> Tuple[Optional[float], Optional[str]]:
        """Check disk usage percentage"""



        try:
            # Get disk usage for database data directory
            data_dir = getattr(self.settings, 'database_data_dir', '/var/lib/postgresql/data')
            usage = psutil.disk_usage(data_dir)
            usage_percent = (usage.used / usage.total) * 100
            return usage_percent, None
        except Exception as e:
            return None, f"Disk usage check failed: {str(e)}"
    
    async def _check_memory_usage(self) -> Tuple[Optional[float], Optional[str]]:
        """Check memory usage percentage"""



        try:
            memory = psutil.virtual_memory()
            return memory.percent, None
        except Exception as e:
            return None, f"Memory usage check failed: {str(e)}"
    
    def _determine_check_status(
        self, 
        check: HealthCheck, 
        value: Optional[float], 
        error: Optional[str]
    ) -> HealthStatus:
        """Determine health status based on value and thresholds"""
        
        if error:
            return HealthStatus.CRITICAL
        
        if value is None:
            return HealthStatus.UNKNOWN
        
        # Apply thresholds (handle both increasing and decreasing metrics)
        if check.critical_threshold is not None:
            if check.warning_threshold is not None:
                # Determine if this is an increasing or decreasing metric
                if check.critical_threshold > check.warning_threshold:
                    # Increasing metric (higher values are worse)
                    if value >= check.critical_threshold:
                        return HealthStatus.CRITICAL
                    elif value >= check.warning_threshold:
                        return HealthStatus.WARNING
                else:
                    # Decreasing metric (lower values are worse)
                    if value <= check.critical_threshold:
                        return HealthStatus.CRITICAL
                    elif value <= check.warning_threshold:
                        return HealthStatus.WARNING
            else:
                # Only critical threshold defined
                if (check.critical_threshold > 50 and value >= check.critical_threshold) or \
                   (check.critical_threshold <= 50 and value <= check.critical_threshold):
                    return HealthStatus.CRITICAL
        
        return HealthStatus.HEALTHY
    
    def _generate_check_message(
        self, 
        check: HealthCheck, 
        status: HealthStatus, 
        value: Optional[float], 
        error: Optional[str]
    ) -> str:
        """Generate human-readable message for check result"""
        
        if error:
            return f"{check.name}: {error}"
        
        if value is None:
            return f"{check.name}: No data available"
        
        status_emoji = {
            HealthStatus.HEALTHY: "",
            HealthStatus.WARNING: "",
            HealthStatus.CRITICAL: "",
            HealthStatus.EMERGENCY: "",
            HealthStatus.UNKNOWN: ""
        }
        
        emoji = status_emoji.get(status, "")
        
        # Format value based on check type
        if "ratio" in check.name.lower() or "percent" in check.name.lower():
            formatted_value = f"{value:.1f}%"
        elif "time" in check.name.lower():
            if value > 3600:
                formatted_value = f"{value/3600:.1f}h"
            elif value > 60:
                formatted_value = f"{value/60:.1f}m"
            else:
                formatted_value = f"{value:.1f}s"
        elif "bytes" in check.name.lower():
            if value > 1e9:
                formatted_value = f"{value/1e9:.1f}GB"
            elif value > 1e6:
                formatted_value = f"{value/1e6:.1f}MB"
            else:
                formatted_value = f"{value:.1f}KB"
        else:
            formatted_value = f"{value:.1f}"
        
        return f"{emoji} {check.name}: {formatted_value}"
    
    async def _store_check_result(self, check_id: str, result: HealthCheckResult) -> None:
        """Store health check result"""



        try:
            # Cache latest result
            await self.cache.set(
                f"health_check:{check_id}",
                json.dumps(result.to_dict()),
                expire=3600
            )
            
            # Store in history (keep last 100 results per check)
            history_key = f"health_history:{check_id}"
            await self.cache.lpush(history_key, json.dumps(result.to_dict()))
            await self.cache.ltrim(history_key, 0, 99)  # Keep last 100
            
        except Exception as e:
            self.logger.error(f"Error storing check result {check_id}: {e}")
    
    async def _generate_health_reports(self) -> None:
        """Generate periodic comprehensive health reports"""
        while self.checking_active:
            try:
                report = await self.generate_health_report()
                if report:
                    self.last_health_report = report
                    self.check_results_history.append(report)
                    
                    # Keep only last 24 reports (24 hours if run hourly)
                    if len(self.check_results_history) > 24:
                        self.check_results_history = self.check_results_history[-24:]
                    
                    # Cache report
                    await self.cache.set(
                        "health_report:latest",
                        json.dumps(report.to_dict()),
                        expire=3600
                    )
                
                await asyncio.sleep(3600)  # Generate report every hour
                
            except Exception as e:
                self.logger.error(f"Error generating health report: {e}")
                await asyncio.sleep(3600)
    
    async def generate_health_report(self) -> Optional[HealthReport]:
        """Generate comprehensive health report"""



        try:
            # Collect all latest check results
            check_results = []
            for check_id in self.health_checks.keys():
                result_data = await self.cache.get(f"health_check:{check_id}")
                if result_data:
                    result_dict = json.loads(result_data)
                    result = HealthCheckResult(
                        check_id=result_dict['check_id'],
                        status=HealthStatus(result_dict['status']),
                        value=result_dict['value'],
                        message=result_dict['message'],
                        details=result_dict['details'],
                        timestamp=datetime.fromisoformat(result_dict['timestamp']),
                        execution_time_ms=result_dict['execution_time_ms'],
                        error=result_dict.get('error')
                    )
                    check_results.append(result)
            
            if not check_results:
                return None
            
            # Calculate overall health status and score
            overall_status, health_score = self._calculate_overall_health(check_results)
            
            # Generate summary by category
            summary_by_category = self._generate_category_summary(check_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(check_results)
            
            report = HealthReport(
                overall_status=overall_status,
                health_score=health_score,
                timestamp=datetime.utcnow(),
                check_results=check_results,
                summary_by_category=summary_by_category,
                recommendations=recommendations,
                metadata={
                    "total_checks": len(check_results),
                    "checks_by_status": {
                        status.value: sum(1 for r in check_results if r.status == status)
                        for status in HealthStatus
                    }
                }
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating health report: {e}")
            return None
    
    def _calculate_overall_health(
        self, 
        check_results: List[HealthCheckResult]
    ) -> Tuple[HealthStatus, float]:
        """Calculate overall health status and numeric score"""
        
        if not check_results:
            return HealthStatus.UNKNOWN, 0.0
        
        # Status weights
        status_weights = {
            HealthStatus.HEALTHY: 100,
            HealthStatus.WARNING: 70,
            HealthStatus.CRITICAL: 30,
            HealthStatus.EMERGENCY: 0,
            HealthStatus.UNKNOWN: 50
        }
        
        # Calculate weighted score
        total_weight = 0
        weighted_sum = 0
        
        critical_count = 0
        warning_count = 0
        
        for result in check_results:
            weight = status_weights.get(result.status, 50)
            total_weight += 1
            weighted_sum += weight
            
            if result.status == HealthStatus.CRITICAL:
                critical_count += 1
            elif result.status == HealthStatus.WARNING:
                warning_count += 1
        
        health_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine overall status
        if critical_count > 0:
            if critical_count >= len(check_results) * 0.3:  # 30% or more critical
                overall_status = HealthStatus.EMERGENCY
            else:
                overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            if warning_count >= len(check_results) * 0.5:  # 50% or more warnings
                overall_status = HealthStatus.CRITICAL
            else:
                overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        return overall_status, health_score
    
    def _generate_category_summary(
        self, 
        check_results: List[HealthCheckResult]
    ) -> Dict[str, Dict[str, Any]]:
        """Generate summary by check category"""
        
        category_results = {}
        for result in check_results:
            category = result.details.get('category', 'unknown')
            
            if category not in category_results:
                category_results[category] = {
                    'checks': [],
                    'status_counts': {status.value: 0 for status in HealthStatus},
                    'overall_status': HealthStatus.HEALTHY,
                    'health_score': 100.0
                }
            
            category_results[category]['checks'].append(result)
            category_results[category]['status_counts'][result.status.value] += 1
        
        # Calculate category health scores
        for category, data in category_results.items():
            overall_status, health_score = self._calculate_overall_health(data['checks'])
            data['overall_status'] = overall_status.value
            data['health_score'] = health_score
            data['total_checks'] = len(data['checks'])
        
        return category_results
    
    def _generate_recommendations(self, check_results: List[HealthCheckResult]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        for result in check_results:
            if result.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                check_id = result.check_id
                
                if check_id == "cache_hit_ratio" and result.value and result.value < 85:
                    recommendations.append(
                        "Consider increasing shared_buffers or optimizing queries to improve cache hit ratio"
                    )
                elif check_id == "active_connections" and result.value and result.value > 80:
                    recommendations.append(
                        "High connection usage detected. Consider connection pooling or reviewing application connection management"
                    )
                elif check_id == "long_running_queries":
                    recommendations.append(
                        "Long-running queries detected. Review query performance and add appropriate indexes"
                    )
                elif check_id == "disk_usage" and result.value and result.value > 90:
                    recommendations.append(
                        "Disk space is running low. Consider cleanup, archiving, or expanding storage"
                    )
                elif check_id == "memory_usage" and result.value and result.value > 90:
                    recommendations.append(
                        "High memory usage detected. Consider optimizing queries or increasing available memory"
                    )
                elif check_id == "replication_lag" and result.value and result.value > 30:
                    recommendations.append(
                        "Replication lag detected. Check network connectivity and replica performance"
                    )
                elif check_id == "bloat_ratio" and result.value and result.value > 25:
                    recommendations.append(
                        "High table bloat detected. Consider running VACUUM FULL or pg_repack on affected tables"
                    )
        
        # Remove duplicates
        return list(set(recommendations))
    
    async def run_health_check_now(self, check_id: str) -> Optional[Dict[str, Any]]:
        """Run specific health check immediately"""



        try:
            check = self.health_checks.get(check_id)
            if not check:
                return {"error": f"Health check {check_id} not found"}
            
            result = await self._execute_health_check(check)
            
            if result:
                await self._store_check_result(check_id, result)
                return result.to_dict()
            else:
                return {"error": f"Failed to execute health check {check_id}"}
                
        except Exception as e:
            self.logger.error(f"Error running health check {check_id}: {e}")
            return {"error": str(e)}
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get current health summary"""



        try:
            if self.last_health_report:
                return {
                    "overall_status": self.last_health_report.overall_status.value,
                    "health_score": self.last_health_report.health_score,
                    "last_check": self.last_health_report.timestamp.isoformat(),
                    "total_checks": len(self.last_health_report.check_results),
                    "checks_by_status": self.last_health_report.metadata.get("checks_by_status", {}),
                    "recommendations_count": len(self.last_health_report.recommendations),
                    "monitoring_active": self.checking_active
                }
            else:
                return {
                    "overall_status": "unknown",
                    "health_score": 0.0,
                    "monitoring_active": self.checking_active,
                    "message": "No health data available"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting health summary: {e}")
            return {"error": str(e)}
    
    async def get_health_check_definitions(self) -> List[Dict[str, Any]]:
        """Get all health check definitions"""



        return [check.to_dict() for check in self.health_checks.values()]
    
    async def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health report history"""



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_reports = [
                report.to_dict() for report in self.check_results_history
                if report.timestamp >= cutoff_time
            ]
            
            return recent_reports
            
        except Exception as e:
            self.logger.error(f"Error getting health history: {e}")
            return []
