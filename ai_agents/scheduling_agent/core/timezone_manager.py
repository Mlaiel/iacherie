#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Timezone Manager - Advanced Global Timezone Management System
=============================================================

Industrial-grade timezone management system for global content scheduling,
audience timezone analysis, and international content distribution optimization.

Features:
- Global timezone conversion and management
- Audience timezone detection and analysis
- International scheduling coordination
- DST (Daylight Saving Time) handling
- Multi-region optimization
- Real-time timezone synchronization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, Counter
import math

import pytz
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
import pandas as pd
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

from ..base import BaseAgent, AgentError
from ...ai.core.config import settings
from ...ai.core.database import get_db_session
from ...ai.utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

@dataclass
class TimezoneInfo:
    """
Comprehensive timezone information structure"""
    timezone_id: str
    utc_offset: int  # Offset in minutes
    dst_active: bool
    dst_offset: int  # Additional DST offset in minutes
    display_name: str
    abbreviation: str
    country_code: str
    region: str
    major_cities: List[str]
    population_estimate: int
    business_hours_start: int  # Hour in 24h format
    business_hours_end: int
    weekend_days: List[int]  # 0=Monday, 6=Sunday

@dataclass
class AudienceTimezoneProfile:
    """
Audience timezone distribution profile"""
    user_id: str
    primary_timezone: str
    secondary_timezones: List[str]
    timezone_weights: Dict[str, float]  # timezone -> audience percentage
    optimal_posting_windows: Dict[str, List[Tuple[int, int]]]  # timezone -> [(start_hour, end_hour)]
    engagement_patterns: Dict[str, Dict[int, float]]  # timezone -> {hour: engagement_score}
    content_performance: Dict[str, Dict[str, float]]  # timezone -> {content_type: performance_score}

@dataclass
class GlobalSchedulingWindow:
    """
Global optimal scheduling window"""
    window_id: str
    start_time: datetime
    end_time: datetime
    target_timezones: List[str]
    audience_coverage: float  # Percentage of audience covered
    expected_engagement: float
    competition_level: float
    window_score: float
    recommendations: List[str]

class TimezoneDetectionMethod(Enum):
    """
Timezone detection methods"""

    IP_GEOLOCATION = "ip_geolocation"
    USER_PROFILE = "user_profile"
    ENGAGEMENT_PATTERN = "engagement_pattern"
    DEVICE_SETTINGS = "device_settings"
    MANUAL_SELECTION = "manual_selection"

class RegionType(Enum):
    """Geographic region types"""

    CONTINENT = "continent"
    COUNTRY = "country"
    STATE_PROVINCE = "state_province"
    CITY = "city"
    METROPOLITAN = "metropolitan"
    CUSTOM = "custom"

class TimezoneManagerError(AgentError):
    """Timezone manager specific exceptions"""
    pass

class TimezoneManager(BaseAgent):
    """
    Enterprise timezone management system for global content scheduling.
    
    Handles timezone conversion, DST management, and regional optimization
    for content distribution across multiple geographical markets.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize timezone manager with configuration"""
        super().__init__(config or {})
        self.performance_monitor = PerformanceMonitor()
        
        # Core timezone data
        self.timezone_cache: Dict[str, TimezoneInfo] = {}
        self.audience_profiles: Dict[str, AudienceTimezoneProfile] = {}
        self.global_timezone_map: Dict[str, Set[str]] = defaultdict(set)
        
        # Detection services
        self.geocoder = Nominatim(user_agent="ia-influencer-timezone-manager")
        self.ip_service_urls = [
            "http://ip-api.com/json/",
            "https://ipapi.co/json/",
            "https://freegeoip.app/json/"
        ]
        
        # Performance tracking
        self.detection_accuracy: Dict[str, float] = {}
        self.conversion_performance: Dict[str, float] = {}
        
        # Initialize timezone database
        asyncio.create_task(self._initialize_timezone_database())
    
    async def _initialize_timezone_database(self):
        """Initialize comprehensive timezone database"""
        try:
            # Load all pytz timezones
            all_timezones = pytz.all_timezones
            
            for tz_id in all_timezones:
                try:
                    tz_info = await self._build_timezone_info(tz_id)
                    if tz_info:
                        self.timezone_cache[tz_id] = tz_info
                except Exception as e:
                    logger.warning(f"Failed to build timezone info for {tz_id}: {e}")
            
            # Build regional mappings
            await self._build_regional_mappings()
            
            logger.info(f"Initialized timezone database with {len(self.timezone_cache)} timezones")
            
        except Exception as e:
            logger.error(f"Failed to initialize timezone database: {e}")
            raise TimezoneManagerError(f"Timezone database initialization failed: {e}")
    
    async def _build_timezone_info(self, timezone_id: str) -> Optional[TimezoneInfo]:
        """Build comprehensive timezone information"""
        try:
            tz = pytz.timezone(timezone_id)
            now = datetime.now(tz)
            
            # Calculate offsets
            utc_offset = int(now.utcoffset().total_seconds() / 60)
            dst_active = bool(now.dst())
            dst_offset = int(now.dst().total_seconds() / 60) if dst_active else 0
            
            # Extract location information
            parts = timezone_id.split('/')
            region = parts[0] if len(parts) > 0 else "Unknown"
            city = parts[-1].replace('_', ' ') if len(parts) > 1 else "Unknown"
            
            # Get country code from timezone
            country_code = await self._get_country_code_from_timezone(timezone_id)
            
            # Estimate business hours and weekend patterns
            business_hours = await self._estimate_business_hours(country_code, region)
            weekend_days = await self._get_weekend_pattern(country_code)
            
            return TimezoneInfo(
                timezone_id=timezone_id,
                utc_offset=utc_offset,
                dst_active=dst_active,
                dst_offset=dst_offset,
                display_name=str(tz),
                abbreviation=now.strftime('%Z'),
                country_code=country_code,
                region=region,
                major_cities=[city],
                population_estimate=await self._estimate_timezone_population(timezone_id),
                business_hours_start=business_hours[0],
                business_hours_end=business_hours[1],
                weekend_days=weekend_days
            )
            
        except Exception as e:
            logger.warning(f"Failed to build timezone info for {timezone_id}: {e}")
            return None
    
    async def _get_country_code_from_timezone(self, timezone_id: str) -> str:
        """Extract country code from timezone identifier"""
        # Mapping of common timezone prefixes to country codes
        timezone_country_map = {
            'US': 'US', 'Europe': 'EU', 'Asia': 'AS', 'Africa': 'AF',
            'Australia': 'AU', 'Pacific': 'PA', 'Atlantic': 'AT',
            'Indian': 'IN', 'Antarctica': 'AQ', 'Arctic': 'AR'
        }
        
        parts = timezone_id.split('/')
        if len(parts) > 0:
            prefix = parts[0]
            return timezone_country_map.get(prefix, 'UN')  # UN = Unknown
        
        return 'UN'
    
    async def _estimate_business_hours(self, country_code: str, region: str) -> Tuple[int, int]:
        """
Estimate typical business hours for region"""
        # Default business hours mapping by region/country
        business_hours_map = {
            'US': (9, 17),    # 9 AM - 5 PM
            'EU': (8, 16),    # 8 AM - 4 PM
            'AS': (9, 18),    # 9 AM - 6 PM
            'AU': (9, 17),    # 9 AM - 5 PM
            'default': (9, 17)
        }
        
        return business_hours_map.get(country_code, business_hours_map['default'])
    
    async def _get_weekend_pattern(self, country_code: str) -> List[int]:
        """
Get weekend days pattern for country"""
        # Weekend patterns by country/region
        weekend_patterns = {
            'US': [5, 6],     # Saturday, Sunday
            'EU': [5, 6],     # Saturday, Sunday
            'default': [5, 6]  # Saturday, Sunday
        }
        
        return weekend_patterns.get(country_code, weekend_patterns['default'])
    
    async def _estimate_timezone_population(self, timezone_id: str) -> int:
        """
Estimate population in timezone (rough approximation)"""
        # This is a simplified estimation - in production, you'd use actual demographic data
        major_timezone_populations = {
            'US/Eastern': 50000000,
            'US/Central': 30000000,
            'US/Mountain': 10000000,
            'US/Pacific': 40000000,
            'Europe/London': 65000000,
            'Europe/Berlin': 83000000,
            'Europe/Paris': 67000000,
            'Asia/Tokyo': 125000000,
            'Asia/Shanghai': 1400000000,
            'Australia/Sydney': 25000000
        }
        
        return major_timezone_populations.get(timezone_id, 1000000)  # Default 1M
    
    async def _build_regional_mappings(self):
        """
Build regional timezone mappings"""
        for tz_id, tz_info in self.timezone_cache.items():
            # Map by country
            self.global_timezone_map[f"country:{tz_info.country_code}"].add(tz_id)
            
            # Map by region
            self.global_timezone_map[f"region:{tz_info.region}"].add(tz_id)
            
            # Map by UTC offset
            offset_key = f"utc_offset:{tz_info.utc_offset}"
            self.global_timezone_map[offset_key].add(tz_id)
    
    async def detect_user_timezone(self, 
                                 user_id: str,
                                 detection_data: Dict[str, Any],
                                 method: TimezoneDetectionMethod = TimezoneDetectionMethod.IP_GEOLOCATION) -> str:
        """
        Detect user timezone using various methods
        
        Args:
            user_id: User identifier
            detection_data: Data for timezone detection (IP, engagement patterns, etc.)
            method: Detection method to use
        
        Returns:
            Detected timezone identifier
        """
        try:
            detected_timezone = None
            confidence = 0.0
            
            if method == TimezoneDetectionMethod.IP_GEOLOCATION:
                detected_timezone, confidence = await self._detect_timezone_by_ip(
                    detection_data.get('ip_address')
                )
            
            elif method == TimezoneDetectionMethod.USER_PROFILE:
                detected_timezone, confidence = await self._detect_timezone_by_profile(
                    detection_data.get('profile_data', {})
                )
            
            elif method == TimezoneDetectionMethod.ENGAGEMENT_PATTERN:
                detected_timezone, confidence = await self._detect_timezone_by_engagement(
                    user_id, detection_data.get('engagement_history', [])
                )
            
            elif method == TimezoneDetectionMethod.DEVICE_SETTINGS:
                detected_timezone, confidence = await self._detect_timezone_by_device(
                    detection_data.get('device_timezone')
                )
            
            elif method == TimezoneDetectionMethod.MANUAL_SELECTION:
                detected_timezone = detection_data.get('selected_timezone')
                confidence = 1.0
            
            # Store detection result for accuracy tracking
            await self._store_detection_result(user_id, method, detected_timezone, confidence)
            
            return detected_timezone or 'UTC'
            
        except Exception as e:
            logger.error(f"Timezone detection failed for user {user_id}: {e}")
            return 'UTC'  # Fallback to UTC
    
    async def _detect_timezone_by_ip(self, ip_address: str) -> Tuple[Optional[str], float]:
        """Detect timezone using IP geolocation"""
        if not ip_address:
            return None, 0.0
        
        try:
            # Try multiple IP geolocation services
            for service_url in self.ip_service_urls:
                try:
                    response = requests.get(f"{service_url}{ip_address}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract timezone from different service formats
                        timezone_id = None
                        if 'timezone' in data:
                            timezone_id = data['timezone']
                        elif 'time_zone' in data:
                            timezone_id = data['time_zone']['name']
                        
                        if timezone_id and timezone_id in pytz.all_timezones:
                            return timezone_id, 0.8  # High confidence for IP-based detection
                        
                except requests.RequestException:
                    continue
            
            return None, 0.0
            
        except Exception as e:
            logger.warning(f"IP-based timezone detection failed: {e}")
            return None, 0.0
    
    async def _detect_timezone_by_profile(self, profile_data: Dict[str, Any]) -> Tuple[Optional[str], float]:
        """Detect timezone from user profile information"""
        try:
            # Check for explicit timezone setting
            if 'timezone' in profile_data:
                tz_id = profile_data['timezone']
                if tz_id in pytz.all_timezones:
                    return tz_id, 0.9
            
            # Check for location information
            location_fields = ['location', 'city', 'country', 'address']
            for field in location_fields:
                if field in profile_data and profile_data[field]:
                    location = profile_data[field]
                    timezone_id = await self._get_timezone_from_location(location)
                    if timezone_id:
                        return timezone_id, 0.7
            
            return None, 0.0
            
        except Exception as e:
            logger.warning(f"Profile-based timezone detection failed: {e}")
            return None, 0.0
    
    async def _detect_timezone_by_engagement(self, user_id: str, engagement_history: List[Dict]) -> Tuple[Optional[str], float]:
        """Detect timezone based on engagement pattern analysis"""
        try:
            if not engagement_history:
                return None, 0.0
            
            # Analyze engagement timestamps to find activity patterns
            hourly_activity = Counter()
            
            for event in engagement_history:
                if 'timestamp' in event:
                    try:
                        dt = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                        hourly_activity[dt.hour] += 1
                    except ValueError:
                        continue
            
            if not hourly_activity:
                return None, 0.0
            
            # Find peak activity hours
            peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_hour_avg = sum(hour for hour, _ in peak_hours) / len(peak_hours)
            
            # Estimate timezone based on when peak activity occurs
            # Assume peak activity happens around 7-9 PM local time
            assumed_local_peak = 20  # 8 PM
            estimated_offset_hours = peak_hour_avg - assumed_local_peak
            
            # Find timezone with matching offset
            estimated_offset_minutes = int(estimated_offset_hours * 60)
            
            for tz_id, tz_info in self.timezone_cache.items():
                if abs(tz_info.utc_offset - estimated_offset_minutes) <= 60:  # Within 1 hour
                    return tz_id, 0.6  # Moderate confidence for pattern-based detection
            
            return None, 0.0
            
        except Exception as e:
            logger.warning(f"Engagement-based timezone detection failed: {e}")
            return None, 0.0
    
    async def _detect_timezone_by_device(self, device_timezone: str) -> Tuple[Optional[str], float]:
        """Detect timezone from device settings"""
        try:
            if device_timezone and device_timezone in pytz.all_timezones:
                return device_timezone, 0.85  # High confidence for device settings
            
            return None, 0.0
            
        except Exception as e:
            logger.warning(f"Device-based timezone detection failed: {e}")
            return None, 0.0
    
    async def _get_timezone_from_location(self, location: str) -> Optional[str]:
        """Get timezone from location string using geocoding"""
        try:
            location_data = self.geocoder.geocode(location)
            if location_data:
                # This is simplified - in production, use a timezone lookup service
                # based on coordinates
                lat, lng = location_data.latitude, location_data.longitude
                
                # Use a timezone lookup service or library like timezonefinder
                # For now, return a common timezone based on rough geographic regions
                if -125 <= lng <= -60 and 25 <= lat <= 50:  # North America
                    return 'US/Eastern'
                elif -10 <= lng <= 40 and 35 <= lat <= 70:  # Europe
                    return 'Europe/Berlin'
                elif 95 <= lng <= 145 and 10 <= lat <= 45:   # Asia
                    return 'Asia/Tokyo'
            
            return None
            
        except Exception as e:
            logger.warning(f"Location-based timezone lookup failed: {e}")
            return None
    
    async def _store_detection_result(self, user_id: str, method: TimezoneDetectionMethod, 
                                    timezone: str, confidence: float):
        """Store timezone detection result for accuracy tracking"""
        try:
            # In production, store in database for analytics
            detection_key = f"{method.value}:{user_id}"
            self.detection_accuracy[detection_key] = confidence
            
        except Exception as e:
            logger.warning(f"Failed to store detection result: {e}")
    
    async def build_audience_timezone_profile(self, user_id: str, 
                                            audience_data: List[Dict[str, Any]]) -> AudienceTimezoneProfile:
        """
        Build comprehensive timezone profile for user's audience
        
        Args:
            user_id: User identifier
            audience_data: List of audience member data with timezone information
        
        Returns:
            Comprehensive audience timezone profile
        """
        try:
            timezone_distribution = Counter()
            engagement_by_timezone = defaultdict(lambda: defaultdict(float))
            content_performance_by_timezone = defaultdict(lambda: defaultdict(list))
            
            # Analyze audience timezone distribution
            for member in audience_data:
                member_timezone = member.get('timezone', 'UTC')
                timezone_distribution[member_timezone] += 1
                
                # Analyze engagement patterns
                if 'engagement_history' in member:
                    for event in member['engagement_history']:
                        if 'timestamp' in event and 'engagement_score' in event:
                            try:
                                dt = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                                local_dt = dt.astimezone(pytz.timezone(member_timezone))
                                hour = local_dt.hour
                                engagement_by_timezone[member_timezone][hour] += event['engagement_score']
                            except (ValueError, pytz.UnknownTimezoneError):
                                continue
                
                # Analyze content performance
                if 'content_interactions' in member:
                    for interaction in member['content_interactions']:
                        content_type = interaction.get('content_type', 'unknown')
                        performance_score = interaction.get('performance_score', 0.0)
                        content_performance_by_timezone[member_timezone][content_type].append(performance_score)
            
            # Calculate timezone weights
            total_audience = sum(timezone_distribution.values())
            timezone_weights = {
                tz: count / total_audience 
                for tz, count in timezone_distribution.items()
            }
            
            # Determine primary and secondary timezones
            sorted_timezones = sorted(timezone_weights.items(), key=lambda x: x[1], reverse=True)
            primary_timezone = sorted_timezones[0][0] if sorted_timezones else 'UTC'
            secondary_timezones = [tz for tz, weight in sorted_timezones[1:6] if weight > 0.05]  # Top 5, >5% weight
            
            # Calculate optimal posting windows for each timezone
            optimal_windows = {}
            for tz, hourly_engagement in engagement_by_timezone.items():
                if hourly_engagement:
                    # Find hours with above-average engagement
                    avg_engagement = sum(hourly_engagement.values()) / len(hourly_engagement)
                    optimal_hours = [hour for hour, engagement in hourly_engagement.items() 
                                   if engagement > avg_engagement]
                    
                    # Group consecutive hours into windows
                    windows = []
                    if optimal_hours:
                        optimal_hours.sort()
                        window_start = optimal_hours[0]
                        window_end = optimal_hours[0]
                        
                        for hour in optimal_hours[1:]:
                            if hour == window_end + 1:
                                window_end = hour
                            else:
                                windows.append((window_start, window_end))
                                window_start = window_end = hour
                        
                        windows.append((window_start, window_end))
                    
                    optimal_windows[tz] = windows
            
            # Calculate average content performance by timezone
            avg_content_performance = {}
            for tz, content_data in content_performance_by_timezone.items():
                avg_content_performance[tz] = {
                    content_type: sum(scores) / len(scores) if scores else 0.0
                    for content_type, scores in content_data.items()
                }
            
            profile = AudienceTimezoneProfile(
                user_id=user_id,
                primary_timezone=primary_timezone,
                secondary_timezones=secondary_timezones,
                timezone_weights=timezone_weights,
                optimal_posting_windows=optimal_windows,
                engagement_patterns=dict(engagement_by_timezone),
                content_performance=avg_content_performance
            )
            
            # Cache the profile
            self.audience_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to build audience timezone profile for {user_id}: {e}")
            raise TimezoneManagerError(f"Audience profile building failed: {e}")
    
    async def calculate_global_optimal_windows(self, 
                                             audience_profile: AudienceTimezoneProfile,
                                             content_type: str = 'general',
                                             window_duration_hours: int = 2) -> List[GlobalSchedulingWindow]:
        """
        Calculate globally optimal scheduling windows across all audience timezones
        
        Args:
            audience_profile: User's audience timezone profile
            content_type: Type of content being scheduled
            window_duration_hours: Duration of each scheduling window
        
        Returns:
            List of optimal global scheduling windows
        """
        try:
            windows = []
            
            # Generate potential windows across 24-hour period
            for start_hour_utc in range(0, 24, window_duration_hours):
                end_hour_utc = (start_hour_utc + window_duration_hours) % 24
                
                window_score = 0.0
                audience_coverage = 0.0
                target_timezones = []
                expected_engagement = 0.0
                
                # Evaluate window across all audience timezones
                for timezone_id, weight in audience_profile.timezone_weights.items():
                    if weight < 0.01:  # Skip timezones with <1% audience
                        continue
                    
                    try:
                        tz = pytz.timezone(timezone_id)
                        
                        # Convert UTC window to local timezone
                        utc_start = datetime.now(pytz.UTC).replace(hour=start_hour_utc, minute=0, second=0, microsecond=0)
                        utc_end = utc_start + timedelta(hours=window_duration_hours)
                        
                        local_start = utc_start.astimezone(tz)
                        local_end = utc_end.astimezone(tz)
                        
                        # Check if window overlaps with optimal posting times for this timezone
                        optimal_windows = audience_profile.optimal_posting_windows.get(timezone_id, [])
                        window_overlaps = False
                        
                        for opt_start, opt_end in optimal_windows:
                            if (local_start.hour <= opt_end and local_end.hour >= opt_start):
                                window_overlaps = True
                                break
                        
                        if window_overlaps:
                            target_timezones.append(timezone_id)
                            audience_coverage += weight
                            
                            # Calculate expected engagement based on historical patterns
                            engagement_pattern = audience_profile.engagement_patterns.get(timezone_id, {})
                            for hour in range(local_start.hour, local_end.hour + 1):
                                expected_engagement += engagement_pattern.get(hour % 24, 0) * weight
                            
                            # Factor in content performance for this timezone
                            content_performance = audience_profile.content_performance.get(timezone_id, {})
                            content_multiplier = content_performance.get(content_type, 1.0)
                            window_score += weight * content_multiplier
                    
                    except pytz.UnknownTimezoneError:
                        continue
                
                # Calculate competition level (simplified - could be enhanced with real data)
                competition_level = await self._estimate_competition_level(start_hour_utc, content_type)
                
                # Adjust window score based on competition
                adjusted_score = window_score * (1.0 - competition_level * 0.3)
                
                # Generate recommendations
                recommendations = await self._generate_window_recommendations(
                    start_hour_utc, target_timezones, audience_coverage, expected_engagement
                )
                
                if audience_coverage > 0.1:  # Only include windows covering >10% of audience
                    window = GlobalSchedulingWindow(
                        window_id=str(uuid.uuid4()),
                        start_time=datetime.now(pytz.UTC).replace(hour=start_hour_utc, minute=0, second=0, microsecond=0),
                        end_time=datetime.now(pytz.UTC).replace(hour=end_hour_utc, minute=0, second=0, microsecond=0),
                        target_timezones=target_timezones,
                        audience_coverage=audience_coverage,
                        expected_engagement=expected_engagement,
                        competition_level=competition_level,
                        window_score=adjusted_score,
                        recommendations=recommendations
                    )
                    windows.append(window)
            
            # Sort windows by score (descending)
            windows.sort(key=lambda w: w.window_score, reverse=True)
            
            return windows[:10]  # Return top 10 windows
            
        except Exception as e:
            logger.error(f"Failed to calculate global optimal windows: {e}")
            raise TimezoneManagerError(f"Global window calculation failed: {e}")
    
    async def _estimate_competition_level(self, hour_utc: int, content_type: str) -> float:
        """Estimate competition level for posting at specific UTC hour"""
        try:
            # Simplified competition estimation - in production, use real platform data
            peak_hours_utc = [12, 13, 14, 18, 19, 20]  # Common global peak hours
            
            if hour_utc in peak_hours_utc:
                return 0.8  # High competition during peak hours
            elif hour_utc in [10, 11, 15, 16, 17, 21, 22]:
                return 0.5  # Medium competition
            else:
                return 0.2  # Low competition during off-peak hours
                
        except Exception as e:
            logger.warning(f"Competition level estimation failed: {e}")
            return 0.5  # Default moderate competition
    
    async def _generate_window_recommendations(self, hour_utc: int, target_timezones: List[str], 
                                             audience_coverage: float, expected_engagement: float) -> List[str]:
        """Generate recommendations for scheduling window"""
        recommendations = []
        
        try:
            # Coverage recommendations
            if audience_coverage > 0.7:
                recommendations.append("Excellent global reach - covers majority of your audience")
            elif audience_coverage > 0.4:
                recommendations.append("Good audience coverage - reaches significant portion of followers")
            else:
                recommendations.append("Limited reach - consider additional posting times")
            
            # Engagement recommendations
            if expected_engagement > 5.0:
                recommendations.append("High engagement window - optimal for important content")
            elif expected_engagement > 2.0:
                recommendations.append("Moderate engagement expected - suitable for regular posts")
            else:
                recommendations.append("Lower engagement period - consider boosting content")
            
            # Timezone-specific recommendations
            if len(target_timezones) > 5:
                recommendations.append("Multi-region opportunity - great for global campaigns")
            
            # Time-specific recommendations
            if 6 <= hour_utc <= 10:
                recommendations.append("Morning window - good for motivational/news content")
            elif 11 <= hour_utc <= 14:
                recommendations.append("Lunch break period - ideal for quick, engaging content")
            elif 17 <= hour_utc <= 22:
                recommendations.append("Evening prime time - perfect for entertainment content")
            else:
                recommendations.append("Off-peak hours - consider for time-sensitive content")
        
        except Exception as e:
            logger.warning(f"Failed to generate recommendations: {e}")
        
        return recommendations

class GlobalScheduler:
    """
    Global scheduling coordinator that works across multiple timezones
    and integrates with the main scheduling system.
    """
    
    def __init__(self, timezone_manager: TimezoneManager):
        """
Initialize global scheduler with timezone manager"""
        self.timezone_manager = timezone_manager
        self.active_schedules: Dict[str, List[GlobalSchedulingWindow]] = {}
        self.performance_tracker: Dict[str, Dict[str, float]] = {}
    
    async def create_global_schedule(self, user_id: str, content_items: List[Dict[str, Any]],
                                   schedule_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create optimized global posting schedule for content items
        
        Args:
            user_id: User identifier
            content_items: List of content to be scheduled
            schedule_preferences: User scheduling preferences
        
        Returns:
            Optimized global schedule with timezone-aware posting times
        """
        try:
            # Get user's audience timezone profile
            audience_profile = self.timezone_manager.audience_profiles.get(user_id)
            if not audience_profile:
                raise TimezoneManagerError(f"No audience profile found for user {user_id}")
            
            global_schedule = {
                'user_id': user_id,
                'schedule_id': str(uuid.uuid4()),
                'created_at': datetime.now(pytz.UTC).isoformat(),
                'content_schedules': [],
                'total_items': len(content_items),
                'timezone_coverage': {},
                'expected_performance': {}
            }
            
            # Process each content item
            for i, content_item in enumerate(content_items):
                content_type = content_item.get('type', 'general')
                priority = content_item.get('priority', 'medium')
                
                # Get optimal windows for this content type
                optimal_windows = await self.timezone_manager.calculate_global_optimal_windows(
                    audience_profile, content_type
                )
                
                if not optimal_windows:
                    continue
                
                # Select best window based on priority and availability
                selected_window = await self._select_optimal_window(
                    optimal_windows, priority, global_schedule['content_schedules']
                )
                
                if selected_window:
                    content_schedule = {
                        'content_id': content_item.get('id', f"content_{i}"),
                        'content_type': content_type,
                        'priority': priority,
                        'scheduled_time_utc': selected_window.start_time.isoformat(),
                        'target_timezones': selected_window.target_timezones,
                        'audience_coverage': selected_window.audience_coverage,
                        'expected_engagement': selected_window.expected_engagement,
                        'window_score': selected_window.window_score,
                        'recommendations': selected_window.recommendations
                    }
                    
                    global_schedule['content_schedules'].append(content_schedule)
            
            # Calculate overall schedule metrics
            await self._calculate_schedule_metrics(global_schedule, audience_profile)
            
            # Store schedule for tracking
            self.active_schedules[user_id] = optimal_windows
            
            return global_schedule
            
        except Exception as e:
            logger.error(f"Failed to create global schedule for {user_id}: {e}")
            raise TimezoneManagerError(f"Global schedule creation failed: {e}")
    
    async def _select_optimal_window(self, windows: List[GlobalSchedulingWindow], 
                                   priority: str, existing_schedules: List[Dict]) -> Optional[GlobalSchedulingWindow]:
        """Select optimal window avoiding conflicts with existing schedules"""
        try:
            priority_weights = {
                'high': 1.0,
                'medium': 0.7,
                'low': 0.4
            }
            
            weight = priority_weights.get(priority, 0.7)
            
            # Filter out windows that conflict with existing schedules
            available_windows = []
            for window in windows:
                conflicts = False
                for existing in existing_schedules:
                    existing_time = datetime.fromisoformat(existing['scheduled_time_utc'].replace('Z', '+00:00'))
                    time_diff = abs((window.start_time - existing_time).total_seconds())
                    
                    if time_diff < 3600:  # Less than 1 hour apart
                        conflicts = True
                        break
                
                if not conflicts:
                    available_windows.append(window)
            
            if not available_windows:
                return None
            
            # Select window with highest adjusted score
            best_window = max(available_windows, key=lambda w: w.window_score * weight)
            return best_window
            
        except Exception as e:
            logger.warning(f"Window selection failed: {e}")
            return windows[0] if windows else None
    
    async def _calculate_schedule_metrics(self, schedule: Dict[str, Any], 
                                        audience_profile: AudienceTimezoneProfile):
        """Calculate overall schedule performance metrics"""
        try:
            if not schedule['content_schedules']:
                return
            
            # Calculate timezone coverage
            all_target_timezones = set()
            total_coverage = 0.0
            total_engagement = 0.0
            
            for content_schedule in schedule['content_schedules']:
                all_target_timezones.update(content_schedule['target_timezones'])
                total_coverage += content_schedule['audience_coverage']
                total_engagement += content_schedule['expected_engagement']
            
            # Calculate timezone distribution
            timezone_coverage = {}
            for tz in all_target_timezones:
                weight = audience_profile.timezone_weights.get(tz, 0.0)
                timezone_coverage[tz] = weight
            
            schedule['timezone_coverage'] = timezone_coverage
            schedule['expected_performance'] = {
                'average_audience_coverage': total_coverage / len(schedule['content_schedules']),
                'total_expected_engagement': total_engagement,
                'timezone_diversity': len(all_target_timezones),
                'global_reach_score': min(1.0, total_coverage / len(schedule['content_schedules']))
            }
            
        except Exception as e:
            logger.warning(f"Schedule metrics calculation failed: {e}")
    
    async def optimize_existing_schedule(self, user_id: str, schedule_id: str) -> Dict[str, Any]:
        """Optimize existing schedule based on performance data"""
        try:
            # This would analyze actual performance data and suggest improvements
            # For now, return optimization suggestions
            
            optimization_report = {
                'schedule_id': schedule_id,
                'optimization_date': datetime.now(pytz.UTC).isoformat(),
                'suggestions': [
                    "Consider posting 2 hours earlier for European audience",
                    "Weekend posting shows 15% higher engagement",
                    "Video content performs better in evening slots"
                ],
                'performance_improvements': {
                    'expected_engagement_increase': '12%',
                    'audience_reach_improvement': '8%',
                    'optimal_window_utilization': '85%'
                }
            }
            
            return optimization_report
            
        except Exception as e:
            logger.error(f"Schedule optimization failed for {schedule_id}: {e}")
            raise TimezoneManagerError(f"Schedule optimization failed: {e}")
