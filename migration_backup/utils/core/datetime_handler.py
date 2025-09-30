"""
DateTime Handler - Core Utilities Level 1
========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade datetime processing utility based on datetime_utilities.py
Enhanced with async operations, performance monitoring, and enterprise standards.

Performance: < 1ms per operation
Standards: 100% async, type hints, timezone-aware operations
"""

import asyncio
import time
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date, time as dt_time, timedelta, timezone
from dataclasses import dataclass, field
import pytz
from dateutil import parser, tz
from dateutil.relativedelta import relativedelta
import calendar
import locale

logger = logging.getLogger(__name__)

@dataclass
class DateTimeResult:
    """Enterprise result container for datetime operations."""
    success: bool
    result: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'result': self.result.isoformat() if isinstance(self.result, (datetime, date)) else self.result,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

class DateTimeHandler:
    """
    Enterprise datetime handler with ultra-high performance standards.
    
    Provides comprehensive datetime operations with timezone awareness,
    business logic, and localization support.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize datetime handler with enterprise configuration."""
        self.config = config or {}
        self._performance_threshold_ms = 1.0
        self._default_timezone = self.config.get('default_timezone', 'UTC')
        self._business_hours_start = self.config.get('business_hours_start', 9)
        self._business_hours_end = self.config.get('business_hours_end', 17)
        self._business_days = set(self.config.get('business_days', [0, 1, 2, 3, 4]))  # Mon-Fri
        
    async def _measure_performance(self, operation: callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    # === CORE DATETIME OPERATIONS ===
    
    async def now_utc(self) -> DateTimeResult:
        """Get current UTC datetime with enterprise precision."""
        def _get_now():
            return datetime.now(timezone.utc)
            
        try:
            result, exec_time = await self._measure_performance(_get_now)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'now_utc', 'timezone': 'UTC'}
            )
        except Exception as e:
            logger.error(f"UTC now operation failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'now_utc'}
            )
    
    async def now_local(self, timezone_name: Optional[str] = None) -> DateTimeResult:
        """Get current local datetime with timezone support."""
        def _get_now_local():
            tz_name = timezone_name or self._default_timezone
            
            if tz_name == 'UTC':
                tz_obj = timezone.utc
            else:
                tz_obj = pytz.timezone(tz_name)
                
            utc_now = datetime.now(timezone.utc)
            return utc_now.astimezone(tz_obj)
            
        try:
            result, exec_time = await self._measure_performance(_get_now_local)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'now_local',
                    'timezone': timezone_name or self._default_timezone
                }
            )
        except Exception as e:
            logger.error(f"Local now operation failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'now_local'}
            )
    
    async def parse_datetime(
        self,
        datetime_string: str,
        format_string: Optional[str] = None,
        timezone_name: Optional[str] = None
    ) -> DateTimeResult:
        """Parse datetime string with intelligent format detection."""
        def _parse():
            if format_string:
                # Use specific format
                parsed = datetime.strptime(datetime_string, format_string)
            else:
                # Intelligent parsing
                parsed = parser.parse(datetime_string)
            
            # Apply timezone if specified
            if timezone_name:
                if parsed.tzinfo is None:
                    if timezone_name == 'UTC':
                        tz_obj = timezone.utc
                    else:
                        tz_obj = pytz.timezone(timezone_name)
                    parsed = parsed.replace(tzinfo=tz_obj)
                else:
                    if timezone_name == 'UTC':
                        tz_obj = timezone.utc
                    else:
                        tz_obj = pytz.timezone(timezone_name)
                    parsed = parsed.astimezone(tz_obj)
            
            return parsed
            
        try:
            result, exec_time = await self._measure_performance(_parse)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'parse_datetime',
                    'input_string': datetime_string,
                    'format_string': format_string,
                    'timezone': timezone_name
                }
            )
        except Exception as e:
            logger.error(f"DateTime parsing failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'parse_datetime'}
            )
    
    async def format_datetime(
        self,
        dt: datetime,
        format_string: str = "%Y-%m-%d %H:%M:%S %Z",
        timezone_name: Optional[str] = None
    ) -> DateTimeResult:
        """Format datetime with timezone conversion and localization."""
        def _format():
            target_dt = dt
            
            # Convert timezone if requested
            if timezone_name:
                if timezone_name == 'UTC':
                    tz_obj = timezone.utc
                else:
                    tz_obj = pytz.timezone(timezone_name)
                target_dt = dt.astimezone(tz_obj)
            
            return target_dt.strftime(format_string)
            
        try:
            result, exec_time = await self._measure_performance(_format)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'format_datetime',
                    'format_string': format_string,
                    'timezone': timezone_name
                }
            )
        except Exception as e:
            logger.error(f"DateTime formatting failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'format_datetime'}
            )
    
    # === TIMEZONE OPERATIONS ===
    
    async def convert_timezone(
        self,
        dt: datetime,
        from_timezone: str,
        to_timezone: str
    ) -> DateTimeResult:
        """Convert datetime between timezones with enterprise accuracy."""
        def _convert():
            # Ensure datetime has timezone info
            if dt.tzinfo is None:
                if from_timezone == 'UTC':
                    from_tz = timezone.utc
                else:
                    from_tz = pytz.timezone(from_timezone)
                dt_with_tz = dt.replace(tzinfo=from_tz)
            else:
                dt_with_tz = dt
            
            # Convert to target timezone
            if to_timezone == 'UTC':
                to_tz = timezone.utc
            else:
                to_tz = pytz.timezone(to_timezone)
                
            return dt_with_tz.astimezone(to_tz)
            
        try:
            result, exec_time = await self._measure_performance(_convert)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'convert_timezone',
                    'from_timezone': from_timezone,
                    'to_timezone': to_timezone
                }
            )
        except Exception as e:
            logger.error(f"Timezone conversion failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'convert_timezone'}
            )
    
    async def get_timezone_info(self, timezone_name: str) -> DateTimeResult:
        """Get comprehensive timezone information."""
        def _get_info():
            if timezone_name == 'UTC':
                tz_obj = timezone.utc
                utc_offset = timedelta(0)
                dst_offset = timedelta(0)
            else:
                tz_obj = pytz.timezone(timezone_name)
                now = datetime.now(tz_obj)
                utc_offset = now.utcoffset()
                dst_offset = now.dst() or timedelta(0)
            
            return {
                'timezone_name': timezone_name,
                'utc_offset_seconds': utc_offset.total_seconds(),
                'utc_offset_hours': utc_offset.total_seconds() / 3600,
                'dst_offset_seconds': dst_offset.total_seconds(),
                'is_dst': dst_offset.total_seconds() > 0,
                'current_time': datetime.now(tz_obj)
            }
            
        try:
            result, exec_time = await self._measure_performance(_get_info)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'get_timezone_info'}
            )
        except Exception as e:
            logger.error(f"Timezone info retrieval failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'get_timezone_info'}
            )
    
    # === BUSINESS DATE OPERATIONS ===
    
    async def is_business_day(self, dt: datetime) -> DateTimeResult:
        """Check if datetime falls on a business day."""
        def _check_business_day():
            weekday = dt.weekday()  # Monday = 0, Sunday = 6
            return weekday in self._business_days
            
        try:
            result, exec_time = await self._measure_performance(_check_business_day)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'is_business_day',
                    'weekday': dt.weekday(),
                    'business_days': list(self._business_days)
                }
            )
        except Exception as e:
            logger.error(f"Business day check failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'is_business_day'}
            )
    
    async def is_business_hours(self, dt: datetime) -> DateTimeResult:
        """Check if datetime falls within business hours."""
        def _check_business_hours():
            hour = dt.hour
            return self._business_hours_start <= hour < self._business_hours_end
            
        try:
            result, exec_time = await self._measure_performance(_check_business_hours)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'is_business_hours',
                    'hour': dt.hour,
                    'business_hours_start': self._business_hours_start,
                    'business_hours_end': self._business_hours_end
                }
            )
        except Exception as e:
            logger.error(f"Business hours check failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'is_business_hours'}
            )
    
    async def next_business_day(
        self,
        dt: datetime,
        skip_count: int = 1
    ) -> DateTimeResult:
        """Get next business day with skip count."""
        def _get_next_business_day():
            current = dt
            days_skipped = 0
            
            while days_skipped < skip_count:
                current += timedelta(days=1)
                if current.weekday() in self._business_days:
                    days_skipped += 1
                    
            return current
            
        try:
            result, exec_time = await self._measure_performance(_get_next_business_day)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'next_business_day',
                    'skip_count': skip_count,
                    'days_advanced': (result - dt).days
                }
            )
        except Exception as e:
            logger.error(f"Next business day calculation failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'next_business_day'}
            )
    
    # === DATE ARITHMETIC OPERATIONS ===
    
    async def add_duration(
        self,
        dt: datetime,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
    ) -> DateTimeResult:
        """Add duration to datetime with enterprise precision."""
        def _add_duration():
            # Use relativedelta for months/years, timedelta for others
            if years or months:
                result = dt + relativedelta(years=years, months=months)
            else:
                result = dt
                
            # Add remaining duration
            delta = timedelta(
                weeks=weeks,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds
            )
            
            return result + delta
            
        try:
            result, exec_time = await self._measure_performance(_add_duration)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'add_duration',
                    'years': years,
                    'months': months,
                    'weeks': weeks,
                    'days': days,
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds
                }
            )
        except Exception as e:
            logger.error(f"Duration addition failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'add_duration'}
            )
    
    async def calculate_age(
        self,
        birth_date: datetime,
        reference_date: Optional[datetime] = None
    ) -> DateTimeResult:
        """Calculate precise age with enterprise accuracy."""
        def _calculate_age():
            ref_date = reference_date or datetime.now(timezone.utc)
            
            # Ensure both dates have same timezone info
            if birth_date.tzinfo != ref_date.tzinfo:
                if birth_date.tzinfo is None:
                    birth_date_tz = birth_date.replace(tzinfo=timezone.utc)
                else:
                    birth_date_tz = birth_date
                    
                if ref_date.tzinfo is None:
                    ref_date_tz = ref_date.replace(tzinfo=timezone.utc)
                else:
                    ref_date_tz = ref_date
            else:
                birth_date_tz = birth_date
                ref_date_tz = ref_date
            
            # Calculate age using relativedelta for precision
            age_delta = relativedelta(ref_date_tz, birth_date_tz)
            
            return {
                'years': age_delta.years,
                'months': age_delta.months,
                'days': age_delta.days,
                'total_days': (ref_date_tz - birth_date_tz).days,
                'total_seconds': (ref_date_tz - birth_date_tz).total_seconds()
            }
            
        try:
            result, exec_time = await self._measure_performance(_calculate_age)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'calculate_age',
                    'birth_date': birth_date.isoformat(),
                    'reference_date': (reference_date or datetime.now(timezone.utc)).isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Age calculation failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'calculate_age'}
            )
    
    # === CALENDAR OPERATIONS ===
    
    async def get_month_info(
        self,
        year: int,
        month: int,
        timezone_name: Optional[str] = None
    ) -> DateTimeResult:
        """Get comprehensive month information."""
        def _get_month_info():
            # Get month boundaries
            first_day = datetime(year, month, 1)
            if month == 12:
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Apply timezone if specified
            if timezone_name:
                if timezone_name == 'UTC':
                    tz_obj = timezone.utc
                else:
                    tz_obj = pytz.timezone(timezone_name)
                    
                first_day = first_day.replace(tzinfo=tz_obj)
                last_day = last_day.replace(tzinfo=tz_obj)
            
            # Get calendar info
            cal = calendar.Calendar()
            month_days = cal.monthdayscalendar(year, month)
            
            # Count business days
            business_days_count = 0
            for week in month_days:
                for day in week:
                    if day > 0:
                        weekday = datetime(year, month, day).weekday()
                        if weekday in self._business_days:
                            business_days_count += 1
            
            return {
                'year': year,
                'month': month,
                'month_name': calendar.month_name[month],
                'first_day': first_day,
                'last_day': last_day,
                'total_days': (last_day - first_day).days + 1,
                'business_days_count': business_days_count,
                'calendar_weeks': month_days,
                'timezone': timezone_name
            }
            
        try:
            result, exec_time = await self._measure_performance(_get_month_info)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'get_month_info'}
            )
        except Exception as e:
            logger.error(f"Month info retrieval failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'get_month_info'}
            )
    
    # === PERFORMANCE UTILITIES ===
    
    async def benchmark_operations(self, iterations: int = 1000) -> DateTimeResult:
        """Benchmark datetime operations for performance validation."""
        async def _benchmark():
            operations = []
            
            # Benchmark now_utc
            start = time.perf_counter()
            for _ in range(iterations):
                await self.now_utc()
            now_utc_time = (time.perf_counter() - start) * 1000 / iterations
            operations.append(('now_utc', now_utc_time))
            
            # Benchmark parsing
            test_date_str = "2023-12-25 15:30:45"
            start = time.perf_counter()
            for _ in range(iterations):
                await self.parse_datetime(test_date_str)
            parse_time = (time.perf_counter() - start) * 1000 / iterations
            operations.append(('parse_datetime', parse_time))
            
            # Benchmark formatting
            test_date = datetime.now(timezone.utc)
            start = time.perf_counter()
            for _ in range(iterations):
                await self.format_datetime(test_date)
            format_time = (time.perf_counter() - start) * 1000 / iterations
            operations.append(('format_datetime', format_time))
            
            return {
                'iterations': iterations,
                'operations': {op: time_ms for op, time_ms in operations},
                'average_time_ms': sum(time_ms for _, time_ms in operations) / len(operations),
                'threshold_ms': self._performance_threshold_ms,
                'all_within_threshold': all(time_ms <= self._performance_threshold_ms for _, time_ms in operations)
            }
            
        try:
            result, exec_time = await self._measure_performance(_benchmark)
            return DateTimeResult(
                success=True,
                result=result,
                execution_time_ms=exec_time,
                metadata={'operation': 'benchmark_operations'}
            )
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return DateTimeResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'benchmark_operations'}
            )

# Enterprise factory pattern for datetime handler
class DateTimeHandlerFactory:
    """Factory for creating configured datetime handler instances."""
    
    @staticmethod
    def create_handler(config: Optional[Dict[str, Any]] = None) -> DateTimeHandler:
        """Create and configure datetime handler."""
        return DateTimeHandler(config)
    
    @staticmethod
    def create_business_handler(
        timezone_name: str = 'UTC',
        business_hours_start: int = 9,
        business_hours_end: int = 17,
        business_days: Optional[List[int]] = None
    ) -> DateTimeHandler:
        """Create datetime handler optimized for business operations."""
        config = {
            'default_timezone': timezone_name,
            'business_hours_start': business_hours_start,
            'business_hours_end': business_hours_end,
            'business_days': business_days or [0, 1, 2, 3, 4]  # Mon-Fri
        }
        return DateTimeHandler(config)