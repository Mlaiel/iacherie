"""
Date and Time Utilities - Enterprise DateTime Management System
==============================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive date and time utilities supporting:
- Timezone-aware datetime operations
- Localization and internationalization
- Business logic datetime calculations
- Performance optimized operations
- Multiple calendar systems support

Expert Roles Covered:
- Backend Senior: DateTime processing and business logic
- DevOps Expert: Timezone management and system integration
- Lead Dev IA: Intelligent datetime parsing and processing
"""

import datetime
import time
import calendar
import re
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from dateutil import parser, tz, relativedelta
from dateutil.easter import easter
import pytz
import locale

logger = logging.getLogger(__name__)


class DateFormat(Enum):
    """Standard date format types"""
    ISO_8601 = "iso_8601"
    US_FORMAT = "us_format"
    EUROPEAN = "european"
    UK_FORMAT = "uk_format"
    ASIAN = "asian"
    RFC_2822 = "rfc_2822"
    UNIX_TIMESTAMP = "unix_timestamp"
    CUSTOM = "custom"


class TimeUnit(Enum):
    """Time unit types for calculations"""
    MICROSECONDS = "microseconds"
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class BusinessDayConvention(Enum):
    """Business day calculation conventions"""
    FOLLOWING = "following"
    PRECEDING = "preceding"
    MODIFIED_FOLLOWING = "modified_following"
    MODIFIED_PRECEDING = "modified_preceding"
    NEAREST = "nearest"


@dataclass
class DateTimeRange:
    """Date/time range with validation"""
    start: datetime.datetime
    end: datetime.datetime
    timezone: Optional[str] = None
    
    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")


@dataclass
class BusinessHours:
    """Business hours configuration"""
    start_time: datetime.time
    end_time: datetime.time
    timezone: str
    working_days: List[int] = None  # 0=Monday, 6=Sunday
    
    def __post_init__(self):
        if self.working_days is None:
            self.working_days = [0, 1, 2, 3, 4]  # Monday to Friday


@dataclass
class HolidayDefinition:
    """Holiday definition"""
    name: str
    date: datetime.date
    country: Optional[str] = None
    region: Optional[str] = None
    is_business_day: bool = False


class DateTimeUtilities:
    """
    Enterprise-grade date and time utilities for international applications.
    
    Features:
    - Timezone-aware operations
    - Business day calculations
    - Holiday management
    - Multiple format support
    - Localization support
    - Performance optimization
    """
    
    def __init__(self,
                 default_timezone: str = "UTC",
                 business_hours: Optional[BusinessHours] = None,
                 holiday_calendar: Optional[List[HolidayDefinition]] = None):
        """
        Initialize datetime utilities
        
        Args:
            default_timezone: Default timezone for operations
            business_hours: Business hours configuration
            holiday_calendar: List of holidays
        """
        try:
            logger.info("Initializing DateTimeUtilities")
            
            # Configuration
            self.default_timezone = pytz.timezone(default_timezone)
            self.business_hours = business_hours or BusinessHours(
                start_time=datetime.time(9, 0),
                end_time=datetime.time(17, 0),
                timezone=default_timezone
            )
            
            # Holiday calendar
            self.holidays = {}
            if holiday_calendar:
                for holiday in holiday_calendar:
                    self.holidays[holiday.date] = holiday
            
            # Format patterns
            self.format_patterns = {
                DateFormat.ISO_8601: "%Y-%m-%dT%H:%M:%S%z",
                DateFormat.US_FORMAT: "%m/%d/%Y %I:%M:%S %p",
                DateFormat.EUROPEAN: "%d.%m.%Y %H:%M:%S",
                DateFormat.UK_FORMAT: "%d/%m/%Y %H:%M:%S",
                DateFormat.ASIAN: "%Y年%m月%d日 %H:%M:%S",
                DateFormat.RFC_2822: "%a, %d %b %Y %H:%M:%S %z"
            }
            
            # Common timezone mappings
            self.timezone_mappings = {
                "EST": "America/New_York",
                "PST": "America/Los_Angeles",
                "CST": "America/Chicago",
                "MST": "America/Denver",
                "GMT": "Europe/London",
                "CET": "Europe/Paris",
                "JST": "Asia/Tokyo",
                "AEST": "Australia/Sydney"
            }
            
            # Performance cache
            self.timezone_cache = {}
            self.format_cache = {}
            
            logger.info("DateTimeUtilities initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DateTimeUtilities: {e}")
            raise

    def now(self, timezone: Optional[str] = None) -> datetime.datetime:
        """
        Get current datetime in specified timezone
        
        Args:
            timezone: Timezone name (defaults to configured timezone)
            
        Returns:
            Current datetime in specified timezone
        """
        tz_obj = self._get_timezone(timezone)
        return datetime.datetime.now(tz_obj)

    def utc_now(self) -> datetime.datetime:
        """
        Get current UTC datetime
        
        Returns:
            Current UTC datetime
        """
        return datetime.datetime.now(pytz.UTC)

    def parse_datetime(self, 
                      date_string: str,
                      format_hint: Optional[DateFormat] = None,
                      timezone: Optional[str] = None,
                      fuzzy: bool = True) -> datetime.datetime:
        """
        Parse datetime string with intelligent format detection
        
        Args:
            date_string: Date/time string to parse
            format_hint: Hint for expected format
            timezone: Timezone to apply if not specified in string
            fuzzy: Whether to use fuzzy parsing
            
        Returns:
            Parsed datetime object
        """
        try:
            logger.debug(f"Parsing datetime string: {date_string}")
            
            # Check cache first
            cache_key = f"{date_string}_{format_hint}_{timezone}_{fuzzy}"
            if cache_key in self.format_cache:
                return self.format_cache[cache_key]
            
            # Handle Unix timestamp
            if date_string.isdigit():
                timestamp = float(date_string)
                dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                if timezone:
                    dt = dt.astimezone(self._get_timezone(timezone))
                self.format_cache[cache_key] = dt
                return dt
            
            # Try specific format if hint provided
            if format_hint and format_hint in self.format_patterns:
                try:
                    dt = datetime.datetime.strptime(date_string, self.format_patterns[format_hint])
                    if not dt.tzinfo and timezone:
                        tz_obj = self._get_timezone(timezone)
                        dt = tz_obj.localize(dt)
                    self.format_cache[cache_key] = dt
                    return dt
                except ValueError:
                    pass  # Fall back to general parsing
            
            # Use dateutil parser for intelligent parsing
            dt = parser.parse(date_string, fuzzy=fuzzy)
            
            # Apply timezone if not present
            if not dt.tzinfo and timezone:
                tz_obj = self._get_timezone(timezone)
                dt = tz_obj.localize(dt)
            elif not dt.tzinfo:
                dt = self.default_timezone.localize(dt)
            
            self.format_cache[cache_key] = dt
            return dt
            
        except Exception as e:
            logger.error(f"Failed to parse datetime string '{date_string}': {e}")
            raise ValueError(f"Unable to parse datetime: {date_string}")

    def format_datetime(self, 
                       dt: datetime.datetime,
                       format_type: DateFormat = DateFormat.ISO_8601,
                       timezone: Optional[str] = None,
                       locale_code: Optional[str] = None) -> str:
        """
        Format datetime to string
        
        Args:
            dt: Datetime to format
            format_type: Format type to use
            timezone: Target timezone for formatting
            locale_code: Locale for formatting (e.g., 'en_US', 'de_DE')
            
        Returns:
            Formatted datetime string
        """
        try:
            # Convert to target timezone if specified
            if timezone:
                target_tz = self._get_timezone(timezone)
                dt = dt.astimezone(target_tz)
            
            # Handle Unix timestamp format
            if format_type == DateFormat.UNIX_TIMESTAMP:
                return str(int(dt.timestamp()))
            
            # Set locale if specified
            old_locale = None
            if locale_code:
                try:
                    old_locale = locale.getlocale()
                    locale.setlocale(locale.LC_TIME, locale_code)
                except:
                    logger.warning(f"Failed to set locale: {locale_code}")
            
            try:
                # Use appropriate format pattern
                if format_type in self.format_patterns:
                    return dt.strftime(self.format_patterns[format_type])
                else:
                    # Default to ISO format
                    return dt.isoformat()
            finally:
                # Restore original locale
                if old_locale:
                    try:
                        locale.setlocale(locale.LC_TIME, old_locale)
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"Failed to format datetime {dt}: {e}")
            return dt.isoformat()  # Fallback

    def convert_timezone(self, 
                        dt: datetime.datetime,
                        target_timezone: str) -> datetime.datetime:
        """
        Convert datetime to different timezone
        
        Args:
            dt: Source datetime
            target_timezone: Target timezone name
            
        Returns:
            Datetime in target timezone
        """
        try:
            target_tz = self._get_timezone(target_timezone)
            
            # Ensure datetime is timezone-aware
            if dt.tzinfo is None:
                dt = self.default_timezone.localize(dt)
            
            return dt.astimezone(target_tz)
            
        except Exception as e:
            logger.error(f"Failed to convert timezone for {dt} to {target_timezone}: {e}")
            raise

    def add_time(self, 
                dt: datetime.datetime,
                unit: TimeUnit,
                amount: int) -> datetime.datetime:
        """
        Add time to datetime
        
        Args:
            dt: Base datetime
            unit: Time unit to add
            amount: Amount to add
            
        Returns:
            New datetime with added time
        """
        try:
            if unit == TimeUnit.MICROSECONDS:
                return dt + datetime.timedelta(microseconds=amount)
            elif unit == TimeUnit.MILLISECONDS:
                return dt + datetime.timedelta(milliseconds=amount)
            elif unit == TimeUnit.SECONDS:
                return dt + datetime.timedelta(seconds=amount)
            elif unit == TimeUnit.MINUTES:
                return dt + datetime.timedelta(minutes=amount)
            elif unit == TimeUnit.HOURS:
                return dt + datetime.timedelta(hours=amount)
            elif unit == TimeUnit.DAYS:
                return dt + datetime.timedelta(days=amount)
            elif unit == TimeUnit.WEEKS:
                return dt + datetime.timedelta(weeks=amount)
            elif unit == TimeUnit.MONTHS:
                return dt + relativedelta.relativedelta(months=amount)
            elif unit == TimeUnit.YEARS:
                return dt + relativedelta.relativedelta(years=amount)
            else:
                raise ValueError(f"Unsupported time unit: {unit}")
                
        except Exception as e:
            logger.error(f"Failed to add {amount} {unit.value} to {dt}: {e}")
            raise

    def subtract_time(self, 
                     dt: datetime.datetime,
                     unit: TimeUnit,
                     amount: int) -> datetime.datetime:
        """
        Subtract time from datetime
        
        Args:
            dt: Base datetime
            unit: Time unit to subtract
            amount: Amount to subtract
            
        Returns:
            New datetime with subtracted time
        """
        return self.add_time(dt, unit, -amount)

    def time_difference(self, 
                       dt1: datetime.datetime,
                       dt2: datetime.datetime,
                       unit: TimeUnit = TimeUnit.SECONDS) -> float:
        """
        Calculate time difference between two datetimes
        
        Args:
            dt1: First datetime
            dt2: Second datetime
            unit: Unit for result
            
        Returns:
            Time difference in specified unit
        """
        try:
            # Ensure both datetimes are timezone-aware
            if dt1.tzinfo is None:
                dt1 = self.default_timezone.localize(dt1)
            if dt2.tzinfo is None:
                dt2 = self.default_timezone.localize(dt2)
            
            delta = dt2 - dt1
            total_seconds = delta.total_seconds()
            
            if unit == TimeUnit.MICROSECONDS:
                return total_seconds * 1_000_000
            elif unit == TimeUnit.MILLISECONDS:
                return total_seconds * 1_000
            elif unit == TimeUnit.SECONDS:
                return total_seconds
            elif unit == TimeUnit.MINUTES:
                return total_seconds / 60
            elif unit == TimeUnit.HOURS:
                return total_seconds / 3600
            elif unit == TimeUnit.DAYS:
                return total_seconds / 86400
            elif unit == TimeUnit.WEEKS:
                return total_seconds / 604800
            else:
                # For months and years, use relativedelta
                rdelta = relativedelta.relativedelta(dt2, dt1)
                if unit == TimeUnit.MONTHS:
                    return rdelta.months + (rdelta.years * 12)
                elif unit == TimeUnit.YEARS:
                    return rdelta.years + (rdelta.months / 12)
                else:
                    return total_seconds
                    
        except Exception as e:
            logger.error(f"Failed to calculate time difference between {dt1} and {dt2}: {e}")
            raise

    def is_business_day(self, 
                       dt: datetime.datetime,
                       country: Optional[str] = None) -> bool:
        """
        Check if datetime falls on a business day
        
        Args:
            dt: Datetime to check
            country: Country for holiday calendar
            
        Returns:
            True if it's a business day
        """
        try:
            # Check if it's a weekend
            if dt.weekday() not in self.business_hours.working_days:
                return False
            
            # Check if it's a holiday
            date_only = dt.date()
            if date_only in self.holidays:
                holiday = self.holidays[date_only]
                if country and holiday.country and holiday.country != country:
                    return True  # Holiday doesn't apply to this country
                return holiday.is_business_day
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check business day for {dt}: {e}")
            return True  # Default to business day

    def next_business_day(self, 
                         dt: datetime.datetime,
                         convention: BusinessDayConvention = BusinessDayConvention.FOLLOWING) -> datetime.datetime:
        """
        Get next business day using specified convention
        
        Args:
            dt: Starting datetime
            convention: Business day convention
            
        Returns:
            Next business day
        """
        try:
            if convention == BusinessDayConvention.FOLLOWING:
                current = dt
                while not self.is_business_day(current):
                    current = self.add_time(current, TimeUnit.DAYS, 1)
                return current
            
            elif convention == BusinessDayConvention.PRECEDING:
                current = dt
                while not self.is_business_day(current):
                    current = self.subtract_time(current, TimeUnit.DAYS, 1)
                return current
            
            elif convention == BusinessDayConvention.MODIFIED_FOLLOWING:
                following = self.next_business_day(dt, BusinessDayConvention.FOLLOWING)
                if following.month != dt.month:
                    return self.next_business_day(dt, BusinessDayConvention.PRECEDING)
                return following
            
            elif convention == BusinessDayConvention.MODIFIED_PRECEDING:
                preceding = self.next_business_day(dt, BusinessDayConvention.PRECEDING)
                if preceding.month != dt.month:
                    return self.next_business_day(dt, BusinessDayConvention.FOLLOWING)
                return preceding
            
            elif convention == BusinessDayConvention.NEAREST:
                following = self.next_business_day(dt, BusinessDayConvention.FOLLOWING)
                preceding = self.next_business_day(dt, BusinessDayConvention.PRECEDING)
                
                if abs((following - dt).days) <= abs((dt - preceding).days):
                    return following
                else:
                    return preceding
            
            else:
                raise ValueError(f"Unsupported business day convention: {convention}")
                
        except Exception as e:
            logger.error(f"Failed to find next business day for {dt}: {e}")
            raise

    def is_within_business_hours(self, dt: datetime.datetime) -> bool:
        """
        Check if datetime is within business hours
        
        Args:
            dt: Datetime to check
            
        Returns:
            True if within business hours
        """
        try:
            # Convert to business hours timezone
            bh_tz = self._get_timezone(self.business_hours.timezone)
            dt_local = dt.astimezone(bh_tz)
            
            # Check if it's a business day
            if not self.is_business_day(dt_local):
                return False
            
            # Check time range
            current_time = dt_local.time()
            return (self.business_hours.start_time <= current_time <= self.business_hours.end_time)
            
        except Exception as e:
            logger.error(f"Failed to check business hours for {dt}: {e}")
            return False

    def get_business_hours_remaining(self, dt: datetime.datetime) -> Optional[datetime.timedelta]:
        """
        Get remaining business hours for the day
        
        Args:
            dt: Current datetime
            
        Returns:
            Remaining business hours or None if not a business day
        """
        try:
            if not self.is_business_day(dt):
                return None
            
            # Convert to business hours timezone
            bh_tz = self._get_timezone(self.business_hours.timezone)
            dt_local = dt.astimezone(bh_tz)
            
            # Create end of business day datetime
            end_of_day = dt_local.replace(
                hour=self.business_hours.end_time.hour,
                minute=self.business_hours.end_time.minute,
                second=self.business_hours.end_time.second,
                microsecond=0
            )
            
            if dt_local >= end_of_day:
                return datetime.timedelta(0)
            
            return end_of_day - dt_local
            
        except Exception as e:
            logger.error(f"Failed to calculate remaining business hours for {dt}: {e}")
            return None

    def create_date_range(self, 
                         start: datetime.datetime,
                         end: datetime.datetime,
                         step: TimeUnit = TimeUnit.DAYS,
                         step_size: int = 1) -> List[datetime.datetime]:
        """
        Create a range of datetimes
        
        Args:
            start: Start datetime
            end: End datetime
            step: Step unit
            step_size: Step size
            
        Returns:
            List of datetimes in range
        """
        try:
            dates = []
            current = start
            
            while current <= end:
                dates.append(current)
                current = self.add_time(current, step, step_size)
            
            return dates
            
        except Exception as e:
            logger.error(f"Failed to create date range from {start} to {end}: {e}")
            return []

    def get_week_boundaries(self, dt: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        Get start and end of week for given datetime
        
        Args:
            dt: Datetime within the week
            
        Returns:
            Tuple of (week_start, week_end)
        """
        try:
            # Monday is 0, Sunday is 6
            days_since_monday = dt.weekday()
            
            week_start = dt - datetime.timedelta(days=days_since_monday)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_end = week_start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
            
            return week_start, week_end
            
        except Exception as e:
            logger.error(f"Failed to get week boundaries for {dt}: {e}")
            raise

    def get_month_boundaries(self, dt: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        Get start and end of month for given datetime
        
        Args:
            dt: Datetime within the month
            
        Returns:
            Tuple of (month_start, month_end)
        """
        try:
            month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get last day of month
            last_day = calendar.monthrange(dt.year, dt.month)[1]
            month_end = dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
            
            return month_start, month_end
            
        except Exception as e:
            logger.error(f"Failed to get month boundaries for {dt}: {e}")
            raise

    def add_holiday(self, holiday: HolidayDefinition):
        """
        Add holiday to calendar
        
        Args:
            holiday: Holiday definition
        """
        self.holidays[holiday.date] = holiday

    def remove_holiday(self, date: datetime.date):
        """
        Remove holiday from calendar
        
        Args:
            date: Holiday date to remove
        """
        if date in self.holidays:
            del self.holidays[date]

    def get_holidays_in_range(self, 
                             start: datetime.date,
                             end: datetime.date,
                             country: Optional[str] = None) -> List[HolidayDefinition]:
        """
        Get holidays within date range
        
        Args:
            start: Start date
            end: End date
            country: Filter by country
            
        Returns:
            List of holidays in range
        """
        holidays = []
        
        for date, holiday in self.holidays.items():
            if start <= date <= end:
                if country is None or holiday.country is None or holiday.country == country:
                    holidays.append(holiday)
        
        return sorted(holidays, key=lambda h: h.date)

    def age_in_years(self, birth_date: datetime.date, reference_date: Optional[datetime.date] = None) -> int:
        """
        Calculate age in years
        
        Args:
            birth_date: Birth date
            reference_date: Reference date (defaults to today)
            
        Returns:
            Age in years
        """
        if reference_date is None:
            reference_date = datetime.date.today()
        
        age = reference_date.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age

    def get_timezone_offset(self, timezone: str, dt: Optional[datetime.datetime] = None) -> datetime.timedelta:
        """
        Get timezone offset from UTC
        
        Args:
            timezone: Timezone name
            dt: Datetime for offset calculation (defaults to now)
            
        Returns:
            Timezone offset
        """
        if dt is None:
            dt = datetime.datetime.now()
        
        tz_obj = self._get_timezone(timezone)
        offset = tz_obj.utcoffset(dt)
        return offset

    def list_available_timezones(self, filter_pattern: Optional[str] = None) -> List[str]:
        """
        List available timezones
        
        Args:
            filter_pattern: Regex pattern to filter timezones
            
        Returns:
            List of timezone names
        """
        timezones = list(pytz.all_timezones)
        
        if filter_pattern:
            pattern = re.compile(filter_pattern, re.IGNORECASE)
            timezones = [tz for tz in timezones if pattern.search(tz)]
        
        return sorted(timezones)

    # Private helper methods
    def _get_timezone(self, timezone: Optional[str] = None) -> pytz.BaseTzInfo:
        """Get timezone object with caching"""
        tz_name = timezone or self.default_timezone.zone
        
        # Check common mappings
        if tz_name in self.timezone_mappings:
            tz_name = self.timezone_mappings[tz_name]
        
        # Check cache
        if tz_name in self.timezone_cache:
            return self.timezone_cache[tz_name]
        
        # Create and cache timezone
        try:
            tz_obj = pytz.timezone(tz_name)
            self.timezone_cache[tz_name] = tz_obj
            return tz_obj
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {tz_name}, using default")
            return self.default_timezone


# Utility functions
def quick_parse_date(date_string: str) -> datetime.datetime:
    """
    Quick date parsing with sensible defaults
    
    Args:
        date_string: Date string to parse
        
    Returns:
        Parsed datetime
    """
    util = DateTimeUtilities()
    return util.parse_datetime(date_string)


def format_relative_time(dt: datetime.datetime, reference: Optional[datetime.datetime] = None) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago")
    
    Args:
        dt: Datetime to format
        reference: Reference datetime (defaults to now)
        
    Returns:
        Relative time string
    """
    if reference is None:
        reference = datetime.datetime.now(dt.tzinfo or pytz.UTC)
    
    delta = reference - dt
    total_seconds = abs(delta.total_seconds())
    
    if total_seconds < 60:
        return "just now"
    elif total_seconds < 3600:
        minutes = int(total_seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif total_seconds < 86400:
        hours = int(total_seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif total_seconds < 604800:
        days = int(total_seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif total_seconds < 2629746:  # ~30.44 days
        weeks = int(total_seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif total_seconds < 31556952:  # ~365.25 days
        months = int(total_seconds // 2629746)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(total_seconds // 31556952)
        return f"{years} year{'s' if years != 1 else ''} ago"


def is_valid_timezone(timezone: str) -> bool:
    """
    Check if timezone name is valid
    
    Args:
        timezone: Timezone name to validate
        
    Returns:
        True if valid timezone
    """
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False


def get_system_timezone() -> str:
    """
    Get system timezone name
    
    Returns:
        System timezone name
    """
    try:
        # Try to get local timezone
        local_tz = tz.tzlocal()
        if hasattr(local_tz, 'zone'):
            return local_tz.zone
        else:
            # Fallback to UTC
            return "UTC"
    except:
        return "UTC"


def sleep_until(target_time: datetime.datetime):
    """
    Sleep until specified datetime
    
    Args:
        target_time: Target datetime to sleep until
    """
    now = datetime.datetime.now(target_time.tzinfo or pytz.UTC)
    if target_time > now:
        sleep_seconds = (target_time - now).total_seconds()
        time.sleep(sleep_seconds)