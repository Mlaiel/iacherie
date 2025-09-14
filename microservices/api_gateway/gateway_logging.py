"""
📝 GATEWAY LOGGING SERVICE - ENTERPRISE MICROSERVICE
Comprehensive logging service for API gateway with structured logging and analytics.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import aiofiles
from pathlib import Path

# Configure structured logging
class GatewayLogLevel(Enum):
    """Gateway log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    service: str
    request_id: str
    endpoint: str
    method: str
    status_code: Optional[int]
    response_time: Optional[float]
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    message: str
    extra_data: Dict[str, Any] = None
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
        
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: GatewayLogLevel = GatewayLogLevel.INFO
    enable_file_logging: bool = True
    enable_redis_logging: bool = True
    enable_console_logging: bool = True
    log_file_path: str = "/var/log/ainflue/gateway.log"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 5
    redis_log_ttl: int = 604800  # 7 days
    buffer_size: int = 1000
    flush_interval: int = 5
    enable_compression: bool = True
    enable_sampling: bool = False
    sampling_rate: float = 0.1

class GatewayLogging:
    """
    📝 Gateway Logging Service
    
    Comprehensive logging service for API gateway with structured logging,
    multiple output destinations, log aggregation, and real-time analytics.
    """
    
    def __init__(self, config: LoggingConfig, redis_url: str = "redis://localhost:6379"):
        self.config = config
        self.redis_url = redis_url
        self.redis = None
        
        # Log buffers
        self.log_buffer: List[LogEntry] = []
        self.error_buffer: List[LogEntry] = []
        
        # Metrics
        self.log_metrics = {
            'total_logs': 0,
            'logs_by_level': {level.value: 0 for level in GatewayLogLevel},
            'logs_by_endpoint': {},
            'error_count': 0,
            'warning_count': 0
        }
        
        # File logging setup
        self.log_file_path = Path(self.config.log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logging
        self._setup_python_logging()
        
        self.running = False
        
    def _setup_python_logging(self):
        """Setup Python logging configuration"""
        # Create custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if self.config.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
            
        # Set log level
        logging.getLogger().setLevel(getattr(logging, self.config.log_level.value))
        
    async def initialize(self):
        """Initialize logging service"""
        try:
            if self.config.enable_redis_logging:
                self.redis = await aioredis.from_url(self.redis_url)
                
            # Start background tasks
            asyncio.create_task(self._log_flush_task())
            asyncio.create_task(self._metrics_update_task())
            asyncio.create_task(self._log_rotation_task())
            
            self.running = True
            await self.log_info("gateway_logging", "Gateway Logging service initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize gateway logging: {e}")
            raise
            
    async def log_request(self, request_id: str, endpoint: str, method: str,
                         ip_address: str, user_agent: str, user_id: Optional[str] = None,
                         extra_data: Optional[Dict[str, Any]] = None):
        """Log incoming request"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=GatewayLogLevel.INFO.value,
            service="gateway",
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=None,
            response_time=None,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            message=f"Incoming {method} request to {endpoint}",
            extra_data=extra_data or {}
        )
        
        await self._add_log_entry(log_entry)
        
    async def log_response(self, request_id: str, endpoint: str, method: str,
                          status_code: int, response_time: float,
                          ip_address: str, user_agent: str, user_id: Optional[str] = None,
                          extra_data: Optional[Dict[str, Any]] = None):
        """Log response"""
        level = GatewayLogLevel.INFO
        if status_code >= 400:
            level = GatewayLogLevel.WARNING if status_code < 500 else GatewayLogLevel.ERROR
            
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level.value,
            service="gateway",
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            message=f"Response {status_code} for {method} {endpoint} in {response_time:.3f}s",
            extra_data=extra_data or {}
        )
        
        await self._add_log_entry(log_entry)
        
    async def log_error(self, request_id: str, endpoint: str, method: str,
                       error: Exception, ip_address: str, user_agent: str,
                       user_id: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
        """Log error"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': self._get_traceback_info(error)
        }
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=GatewayLogLevel.ERROR.value,
            service="gateway",
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            status_code=None,
            response_time=None,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            message=f"Error in {method} {endpoint}: {error}",
            extra_data=extra_data or {},
            error_details=error_details
        )
        
        await self._add_log_entry(log_entry)
        self.error_buffer.append(log_entry)
        
    async def log_info(self, service: str, message: str, request_id: str = "",
                      extra_data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=GatewayLogLevel.INFO.value,
            service=service,
            request_id=request_id,
            endpoint="",
            method="",
            status_code=None,
            response_time=None,
            user_id=None,
            ip_address="",
            user_agent="",
            message=message,
            extra_data=extra_data or {}
        )
        
        await self._add_log_entry(log_entry)
        
    async def log_warning(self, service: str, message: str, request_id: str = "",
                         extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=GatewayLogLevel.WARNING.value,
            service=service,
            request_id=request_id,
            endpoint="",
            method="",
            status_code=None,
            response_time=None,
            user_id=None,
            ip_address="",
            user_agent="",
            message=message,
            extra_data=extra_data or {}
        )
        
        await self._add_log_entry(log_entry)
        
    async def log_critical(self, service: str, message: str, request_id: str = "",
                          extra_data: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=GatewayLogLevel.CRITICAL.value,
            service=service,
            request_id=request_id,
            endpoint="",
            method="",
            status_code=None,
            response_time=None,
            user_id=None,
            ip_address="",
            user_agent="",
            message=message,
            extra_data=extra_data or {}
        )
        
        await self._add_log_entry(log_entry)
        
    async def _add_log_entry(self, log_entry: LogEntry):
        """Add log entry to buffer"""
        # Apply sampling if enabled
        if self.config.enable_sampling:
            import random
            if random.random() > self.config.sampling_rate:
                return
                
        self.log_buffer.append(log_entry)
        
        # Update metrics
        self.log_metrics['total_logs'] += 1
        self.log_metrics['logs_by_level'][log_entry.level] += 1
        
        if log_entry.endpoint:
            if log_entry.endpoint not in self.log_metrics['logs_by_endpoint']:
                self.log_metrics['logs_by_endpoint'][log_entry.endpoint] = 0
            self.log_metrics['logs_by_endpoint'][log_entry.endpoint] += 1
            
        if log_entry.level == GatewayLogLevel.ERROR.value:
            self.log_metrics['error_count'] += 1
        elif log_entry.level == GatewayLogLevel.WARNING.value:
            self.log_metrics['warning_count'] += 1
            
        # Console logging
        if self.config.enable_console_logging:
            print(log_entry.to_json())
            
        # Immediate flush for critical logs
        if log_entry.level == GatewayLogLevel.CRITICAL.value:
            await self._flush_logs()
            
    def _get_traceback_info(self, error: Exception) -> str:
        """Get traceback information from exception"""
        import traceback
        return traceback.format_exc()
        
    async def _flush_logs(self):
        """Flush log buffer to destinations"""
        if not self.log_buffer:
            return
            
        logs_to_flush = self.log_buffer.copy()
        self.log_buffer.clear()
        
        # File logging
        if self.config.enable_file_logging:
            await self._write_to_file(logs_to_flush)
            
        # Redis logging
        if self.config.enable_redis_logging and self.redis:
            await self._write_to_redis(logs_to_flush)
            
    async def _write_to_file(self, log_entries: List[LogEntry]):
        """Write logs to file"""
        try:
            async with aiofiles.open(self.log_file_path, 'a') as f:
                for entry in log_entries:
                    await f.write(entry.to_json() + '\n')
                    
        except Exception as e:
            print(f"Failed to write logs to file: {e}")
            
    async def _write_to_redis(self, log_entries: List[LogEntry]):
        """Write logs to Redis"""
        try:
            pipe = self.redis.pipeline()
            
            for entry in log_entries:
                # Store in multiple Redis structures for different query patterns
                
                # Timeline logs
                pipe.zadd(
                    "gateway:logs:timeline",
                    {entry.to_json(): entry.timestamp.timestamp()}
                )
                
                # Logs by level
                pipe.lpush(f"gateway:logs:level:{entry.level}", entry.to_json())
                pipe.expire(f"gateway:logs:level:{entry.level}", self.config.redis_log_ttl)
                
                # Logs by endpoint
                if entry.endpoint:
                    pipe.lpush(f"gateway:logs:endpoint:{entry.endpoint}", entry.to_json())
                    pipe.expire(f"gateway:logs:endpoint:{entry.endpoint}", self.config.redis_log_ttl)
                    
                # Logs by request ID
                if entry.request_id:
                    pipe.lpush(f"gateway:logs:request:{entry.request_id}", entry.to_json())
                    pipe.expire(f"gateway:logs:request:{entry.request_id}", 3600)  # 1 hour
                    
                # Error logs (special collection)
                if entry.level in [GatewayLogLevel.ERROR.value, GatewayLogLevel.CRITICAL.value]:
                    pipe.lpush("gateway:logs:errors", entry.to_json())
                    pipe.expire("gateway:logs:errors", self.config.redis_log_ttl)
                    
            # Execute pipeline
            await pipe.execute()
            
            # Clean up old timeline entries
            cutoff_time = (datetime.utcnow() - timedelta(seconds=self.config.redis_log_ttl)).timestamp()
            await self.redis.zremrangebyscore("gateway:logs:timeline", 0, cutoff_time)
            
        except Exception as e:
            print(f"Failed to write logs to Redis: {e}")
            
    async def get_logs(self, level: Optional[str] = None, endpoint: Optional[str] = None,
                      request_id: Optional[str] = None, start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve logs based on filters"""
        if not self.redis:
            return []
            
        try:
            if request_id:
                # Get logs for specific request
                logs = await self.redis.lrange(f"gateway:logs:request:{request_id}", 0, limit - 1)
                
            elif level:
                # Get logs by level
                logs = await self.redis.lrange(f"gateway:logs:level:{level}", 0, limit - 1)
                
            elif endpoint:
                # Get logs by endpoint
                logs = await self.redis.lrange(f"gateway:logs:endpoint:{endpoint}", 0, limit - 1)
                
            else:
                # Get from timeline
                if start_time and end_time:
                    start_ts = start_time.timestamp()
                    end_ts = end_time.timestamp()
                    logs = await self.redis.zrevrangebyscore(
                        "gateway:logs:timeline", end_ts, start_ts, offset=0, count=limit
                    )
                else:
                    logs = await self.redis.zrevrange("gateway:logs:timeline", 0, limit - 1)
                    
            # Parse JSON logs
            parsed_logs = []
            for log_data in logs:
                if isinstance(log_data, bytes):
                    log_data = log_data.decode('utf-8')
                try:
                    parsed_logs.append(json.loads(log_data))
                except json.JSONDecodeError:
                    continue
                    
            return parsed_logs
            
        except Exception as e:
            print(f"Failed to retrieve logs: {e}")
            return []
            
    async def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent error logs
        error_logs = await self.get_logs(level="ERROR", start_time=start_time, limit=1000)
        critical_logs = await self.get_logs(level="CRITICAL", start_time=start_time, limit=1000)
        
        # Analyze errors
        error_analysis = {
            'total_errors': len(error_logs),
            'total_critical': len(critical_logs),
            'errors_by_endpoint': {},
            'errors_by_type': {},
            'error_timeline': {},
            'top_errors': []
        }
        
        all_errors = error_logs + critical_logs
        
        for log_entry in all_errors:
            # Count by endpoint
            endpoint = log_entry.get('endpoint', 'unknown')
            if endpoint not in error_analysis['errors_by_endpoint']:
                error_analysis['errors_by_endpoint'][endpoint] = 0
            error_analysis['errors_by_endpoint'][endpoint] += 1
            
            # Count by error type
            error_details = log_entry.get('error_details', {})
            error_type = error_details.get('error_type', 'unknown')
            if error_type not in error_analysis['errors_by_type']:
                error_analysis['errors_by_type'][error_type] = 0
            error_analysis['errors_by_type'][error_type] += 1
            
            # Timeline (hourly buckets)
            timestamp = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
            hour_bucket = timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
            if hour_bucket not in error_analysis['error_timeline']:
                error_analysis['error_timeline'][hour_bucket] = 0
            error_analysis['error_timeline'][hour_bucket] += 1
            
        # Sort and limit top errors
        error_analysis['errors_by_endpoint'] = dict(
            sorted(error_analysis['errors_by_endpoint'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        error_analysis['errors_by_type'] = dict(
            sorted(error_analysis['errors_by_type'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        return error_analysis
        
    async def get_log_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        return {
            **self.log_metrics,
            'buffer_size': len(self.log_buffer),
            'error_buffer_size': len(self.error_buffer),
            'redis_available': self.redis is not None,
            'log_file_size': self.log_file_path.stat().st_size if self.log_file_path.exists() else 0
        }
        
    async def _log_flush_task(self):
        """Background task for flushing logs"""
        while self.running:
            try:
                await self._flush_logs()
                await asyncio.sleep(self.config.flush_interval)
            except Exception as e:
                print(f"Error in log flush task: {e}")
                await asyncio.sleep(10)
                
    async def _metrics_update_task(self):
        """Background task for updating log metrics"""
        while self.running:
            try:
                if self.redis:
                    metrics = await self.get_log_metrics()
                    await self.redis.setex(
                        "gateway:logging:metrics", 
                        60, 
                        json.dumps(metrics, default=str)
                    )
                    
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                print(f"Error in log metrics update task: {e}")
                await asyncio.sleep(60)
                
    async def _log_rotation_task(self):
        """Background task for log file rotation"""
        while self.running:
            try:
                if (self.config.enable_file_logging and 
                    self.log_file_path.exists() and 
                    self.log_file_path.stat().st_size > self.config.max_file_size):
                    
                    # Rotate log file
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    backup_path = self.log_file_path.with_suffix(f".{timestamp}.log")
                    
                    # Move current log to backup
                    self.log_file_path.rename(backup_path)
                    
                    # Compress if enabled
                    if self.config.enable_compression:
                        import gzip
                        with open(backup_path, 'rb') as f_in:
                            with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                                f_out.writelines(f_in)
                        backup_path.unlink()  # Remove uncompressed file
                        
                    await self.log_info("gateway_logging", f"Log file rotated to {backup_path}")
                    
                    # Clean up old backups
                    await self._cleanup_old_backups()
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"Error in log rotation task: {e}")
                await asyncio.sleep(600)
                
    async def _cleanup_old_backups(self):
        """Clean up old log backup files"""
        try:
            backup_files = list(self.log_file_path.parent.glob(f"{self.log_file_path.stem}.*.log*"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backup_count files
            for old_backup in backup_files[self.config.backup_count:]:
                old_backup.unlink()
                await self.log_info("gateway_logging", f"Cleaned up old backup: {old_backup}")
                
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check for logging service"""
        redis_status = "healthy"
        if self.config.enable_redis_logging:
            try:
                if self.redis:
                    await self.redis.ping()
                else:
                    redis_status = "not_configured"
            except Exception as e:
                redis_status = f"unhealthy: {e}"
                
        file_status = "healthy"
        if self.config.enable_file_logging:
            try:
                # Check if log directory is writable
                test_file = self.log_file_path.parent / ".write_test"
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                file_status = f"unhealthy: {e}"
                
        return {
            'service': 'gateway_logging',
            'status': 'healthy' if redis_status == "healthy" and file_status == "healthy" else 'degraded',
            'redis': redis_status,
            'file_logging': file_status,
            'buffer_size': len(self.log_buffer),
            'total_logs': self.log_metrics['total_logs'],
            'error_count': self.log_metrics['error_count']
        }
        
    async def shutdown(self):
        """Shutdown logging service"""
        self.running = False
        
        # Flush remaining logs
        await self._flush_logs()
        
        if self.redis:
            await self.redis.close()
            
        await self.log_info("gateway_logging", "Gateway Logging service shut down")

# Example usage
async def create_gateway_logging():
    """Factory function to create gateway logging service"""
    config = LoggingConfig(
        log_level=GatewayLogLevel.INFO,
        enable_file_logging=True,
        enable_redis_logging=True,
        enable_console_logging=True
    )
    
    logging_service = GatewayLogging(config)
    await logging_service.initialize()
    
    return logging_service

if __name__ == "__main__":
    async def main():
        logging_service = await create_gateway_logging()
        
        # Example usage
        await logging_service.log_request(
            "req_123", "/api/v1/creators", "GET", 
            "192.168.1.100", "Mozilla/5.0...", "user_456"
        )
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        await logging_service.log_response(
            "req_123", "/api/v1/creators", "GET", 
            200, 0.15, "192.168.1.100", "Mozilla/5.0...", "user_456"
        )
        
        # Log an error
        try:
            raise ValueError("Example error")
        except ValueError as e:
            await logging_service.log_error(
                "req_124", "/api/v1/creators", "POST", 
                e, "192.168.1.101", "Mozilla/5.0..."
            )
            
        # Wait for logs to be flushed
        await asyncio.sleep(6)
        
        # Get logs
        logs = await logging_service.get_logs(limit=10)
        print("Recent logs:", logs)
        
        # Get error summary
        error_summary = await logging_service.get_error_summary()
        print("Error summary:", error_summary)
        
        await logging_service.shutdown()
        
    asyncio.run(main())