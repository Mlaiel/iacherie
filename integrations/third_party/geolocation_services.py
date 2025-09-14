"""
Geolocation Services module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Platform - Geolocation Services Integration Module
Enterprise-grade geolocation services for location-based content and analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Integration-Level: Level 3 (integrations/third_party/)
Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
Location Focus: Geo-targeting, regional content, local monetization, compliance by region
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import structlog
from pydantic import BaseModel, Field, validator
import requests
import math

# Configure structured logging
logger = structlog.get_logger(__name__)

class GeolocationProvider(str, Enum):
    """Supported geolocation providers"""
    GOOGLE_MAPS = "google_maps"
    MAPBOX = "mapbox"
    HERE_MAPS = "here_maps"
    OPENCAGE = "opencage"
    IPAPI = "ipapi"
    IPGEOLOCATION = "ipgeolocation"
    MAXMIND = "maxmind"
    IPINFO = "ipinfo"
    LOCATIONIQ = "locationiq"

class LocationType(str, Enum):
    """Types of location data"""
    IP_ADDRESS = "ip_address"
    COORDINATES = "coordinates"
    ADDRESS = "address"
    PLACE_NAME = "place_name"
    POSTAL_CODE = "postal_code"
    DEVICE_LOCATION = "device_location"

class RegionType(str, Enum):
    """Geographic region types"""
    CONTINENT = "continent"
    COUNTRY = "country"
    STATE_PROVINCE = "state_province"
    CITY = "city"
    DISTRICT = "district"
    NEIGHBORHOOD = "neighborhood"
    POSTAL_AREA = "postal_area"

@dataclass
class Coordinates:
    """Geographic coordinates"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None  # in meters
    altitude: Optional[float] = None  # in meters
    heading: Optional[float] = None  # direction in degrees
    speed: Optional[float] = None  # in m/s

@dataclass
class Address:
    """Structured address data"""
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    formatted_address: Optional[str] = None
    address_components: Dict[str, str] = field(default_factory=dict)

@dataclass
class LocationData:
    """Complete location information"""
    coordinates: Optional[Coordinates] = None
    address: Optional[Address] = None
    timezone: Optional[str] = None
    timezone_offset: Optional[int] = None  # UTC offset in seconds
    currency: Optional[str] = None
    language: Optional[str] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    as_number: Optional[str] = None
    threat_level: str = "none"  # none, low, medium, high
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    is_mobile: bool = False
    accuracy_radius: Optional[int] = None  # in km
    confidence_score: float = 0.0

class GeolocationRequest(BaseModel):
    """Geolocation request structure"""
    input_data: str  # IP, coordinates, address, etc.
    input_type: LocationType = LocationType.IP_ADDRESS
    provider: Optional[GeolocationProvider] = None
    include_timezone: bool = True
    include_currency: bool = True
    include_isp: bool = False
    include_security: bool = False
    language: str = "en"
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GeolocationResponse(BaseModel):
    """Geolocation response structure"""
    request_id: str
    success: bool = True
    location_data: Optional[LocationData] = None
    provider: GeolocationProvider
    processing_time: float = 0.0
    cost: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GoogleMapsAPI:
    """Google Maps Platform APIs integration"""
    
    def __init__(self, api_key -> None: str) -> None:
        self.api_key = api_key
        self.base_urls = {
            "geocoding": "https://maps.googleapis.com/maps/api/geocode/json",
            "reverse_geocoding": "https://maps.googleapis.com/maps/api/geocode/json",
            "timezone": "https://maps.googleapis.com/maps/api/timezone/json",
            "places": "https://maps.googleapis.com/maps/api/place/textsearch/json"
        }
        self.session = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
            
    async def geocode_address(self, address: str, request: GeolocationRequest) -> GeolocationResponse:
        """Geocode address to coordinates"""
        try:
            start_time = time.time()
            
            params = {
                "address": address,
                "key": self.api_key,
                "language": request.language
            }
            
            async with self.session.get(self.base_urls["geocoding"], params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK" and data["results"]:
                        result = data["results"][0]
                        geometry = result["geometry"]
                        
                        # Extract coordinates
                        coordinates = Coordinates(
                            latitude=geometry["location"]["lat"],
                            longitude=geometry["location"]["lng"]
                        )
                        
                        # Extract address components
                        address_data = self._parse_address_components(result["address_components"])
                        address_data.formatted_address = result["formatted_address"]
                        
                        # Get timezone if requested
                        timezone_info = None
                        if request.include_timezone:
                            timezone_info = await self._get_timezone(coordinates)
                            
                        location_data = LocationData(
                            coordinates=coordinates,
                            address=address_data,
                            timezone=timezone_info.get("timeZoneId") if timezone_info else None,
                            timezone_offset=timezone_info.get("rawOffset") if timezone_info else None,
                            confidence_score=0.9
                        )
                        
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=True,
                            location_data=location_data,
                            provider=GeolocationProvider.GOOGLE_MAPS,
                            processing_time=processing_time,
                            cost=self._calculate_cost("geocoding")
                        )
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider.GOOGLE_MAPS,
                            error_message=f"Geocoding failed: {data['status']}"
                        )
                else:
                    return GeolocationResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=GeolocationProvider.GOOGLE_MAPS,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("Google Maps geocoding failed", error=str(e))
            return GeolocationResponse(
                request_id=request.request_id,
                success=False,
                provider=GeolocationProvider.GOOGLE_MAPS,
                error_message=str(e)
            )
            
    async def reverse_geocode(self, coordinates: Coordinates, request: GeolocationRequest) -> GeolocationResponse:
        """Reverse geocode coordinates to address"""
        try:
            start_time = time.time()
            
            params = {
                "latlng": f"{coordinates.latitude},{coordinates.longitude}",
                "key": self.api_key,
                "language": request.language
            }
            
            async with self.session.get(self.base_urls["reverse_geocoding"], params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK" and data["results"]:
                        result = data["results"][0]
                        
                        # Parse address
                        address_data = self._parse_address_components(result["address_components"])
                        address_data.formatted_address = result["formatted_address"]
                        
                        # Get timezone
                        timezone_info = None
                        if request.include_timezone:
                            timezone_info = await self._get_timezone(coordinates)
                            
                        location_data = LocationData(
                            coordinates=coordinates,
                            address=address_data,
                            timezone=timezone_info.get("timeZoneId") if timezone_info else None,
                            timezone_offset=timezone_info.get("rawOffset") if timezone_info else None,
                            confidence_score=0.9
                        )
                        
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=True,
                            location_data=location_data,
                            provider=GeolocationProvider.GOOGLE_MAPS,
                            processing_time=processing_time,
                            cost=self._calculate_cost("reverse_geocoding")
                        )
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider.GOOGLE_MAPS,
                            error_message=f"Reverse geocoding failed: {data['status']}"
                        )
                else:
                    return GeolocationResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=GeolocationProvider.GOOGLE_MAPS,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("Google Maps reverse geocoding failed", error=str(e))
            return GeolocationResponse(
                request_id=request.request_id,
                success=False,
                provider=GeolocationProvider.GOOGLE_MAPS,
                error_message=str(e)
            )
            
    async def _get_timezone(self, coordinates: Coordinates) -> Optional[Dict[str, Any]]:
        """Get timezone information for coordinates"""
        try:
            params = {
                "location": f"{coordinates.latitude},{coordinates.longitude}",
                "timestamp": int(time.time()),
                "key": self.api_key
            }
            
            async with self.session.get(self.base_urls["timezone"], params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "OK":
                        return data
                return None
                
        except Exception as e:
            logger.error("Timezone lookup failed", error=str(e))
            return None
            
    def _parse_address_components(self, components: List[Dict[str, Any]]) -> Address:
        """Parse Google Maps address components"""
        address = Address()
        
        component_mapping = {
            "street_number": "street_number",
            "route": "street_name",
            "locality": "city",
            "administrative_area_level_1": "state_province",
            "postal_code": "postal_code",
            "country": "country"
        }
        
        for component in components:
            types = component["types"]
            long_name = component["long_name"]
            short_name = component["short_name"]
            
            for component_type in types:
                if component_type in component_mapping:
                    attr_name = component_mapping[component_type]
                    if component_type == "country":
                        address.country = long_name
                        address.country_code = short_name
                    else:
                        setattr(address, attr_name, long_name)
                        
        return address
        
    def _calculate_cost(self, operation: str) -> float:
        """Calculate Google Maps API cost"""
        # Google Maps pricing (simplified)
        costs = {
            "geocoding": 0.005,  # $5 per 1000 requests
            "reverse_geocoding": 0.005,
            "timezone": 0.005
        }
        return costs.get(operation, 0.005)

class IPAPIService:
    """IP-API.com service for IP geolocation"""
    
    def __init__(self, api_key -> None: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = "http://ip-api.com/json" if not api_key else "https://pro.ip-api.com/json"
        self.session = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
            
    async def geolocate_ip(self, ip_address: str, request: GeolocationRequest) -> GeolocationResponse:
        """Geolocate IP address"""
        try:
            start_time = time.time()
            
            url = f"{self.base_url}/{ip_address}"
            params = {
                "fields": "status,message,continent,continentCode,country,countryCode,region,regionName,city,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
            }
            
            if self.api_key:
                params["key"] = self.api_key
                
            async with self.session.get(url, params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "success":
                        coordinates = Coordinates(
                            latitude=data["lat"],
                            longitude=data["lon"]
                        )
                        
                        address = Address(
                            city=data.get("city"),
                            state_province=data.get("regionName"),
                            postal_code=data.get("zip"),
                            country=data.get("country"),
                            country_code=data.get("countryCode")
                        )
                        
                        location_data = LocationData(
                            coordinates=coordinates,
                            address=address,
                            timezone=data.get("timezone"),
                            timezone_offset=data.get("offset"),
                            currency=data.get("currency"),
                            isp=data.get("isp"),
                            organization=data.get("org"),
                            as_number=data.get("as"),
                            is_proxy=data.get("proxy", False),
                            is_mobile=data.get("mobile", False),
                            confidence_score=0.8
                        )
                        
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=True,
                            location_data=location_data,
                            provider=GeolocationProvider.IPAPI,
                            processing_time=processing_time,
                            cost=0.0 if not self.api_key else 0.001
                        )
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider.IPAPI,
                            error_message=data.get("message", "IP geolocation failed")
                        )
                else:
                    return GeolocationResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=GeolocationProvider.IPAPI,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("IP-API geolocation failed", error=str(e))
            return GeolocationResponse(
                request_id=request.request_id,
                success=False,
                provider=GeolocationProvider.IPAPI,
                error_message=str(e)
            )

class MapboxAPI:
    """Mapbox APIs integration"""
    
    def __init__(self, access_token -> None: str) -> None:
        self.access_token = access_token
        self.base_urls = {
            "geocoding": "https://api.mapbox.com/geocoding/v5/mapbox.places",
            "directions": "https://api.mapbox.com/directions/v5/mapbox",
            "isochrone": "https://api.mapbox.com/isochrone/v1/mapbox"
        }
        self.session = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
            
    async def geocode(self, query: str, request: GeolocationRequest) -> GeolocationResponse:
        """Geocode using Mapbox"""
        try:
            start_time = time.time()
            
            url = f"{self.base_urls['geocoding']}/{query}.json"
            params = {
                "access_token": self.access_token,
                "language": request.language,
                "limit": 1
            }
            
            async with self.session.get(url, params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data["features"]:
                        feature = data["features"][0]
                        geometry = feature["geometry"]
                        properties = feature["properties"]
                        
                        coordinates = Coordinates(
                            latitude=geometry["coordinates"][1],
                            longitude=geometry["coordinates"][0]
                        )
                        
                        # Parse address from context
                        address = self._parse_mapbox_context(feature.get("context", []))
                        address.formatted_address = feature.get("place_name")
                        
                        location_data = LocationData(
                            coordinates=coordinates,
                            address=address,
                            confidence_score=0.85
                        )
                        
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=True,
                            location_data=location_data,
                            provider=GeolocationProvider.MAPBOX,
                            processing_time=processing_time,
                            cost=self._calculate_cost("geocoding")
                        )
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider.MAPBOX,
                            error_message="No results found"
                        )
                else:
                    return GeolocationResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=GeolocationProvider.MAPBOX,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("Mapbox geocoding failed", error=str(e))
            return GeolocationResponse(
                request_id=request.request_id,
                success=False,
                provider=GeolocationProvider.MAPBOX,
                error_message=str(e)
            )
            
    def _parse_mapbox_context(self, context: List[Dict[str, Any]]) -> Address:
        """Parse Mapbox context to address"""
        address = Address()
        
        for item in context:
            item_id = item.get("id", "")
            text = item.get("text", "")
            
            if "postcode" in item_id:
                address.postal_code = text
            elif "place" in item_id:
                address.city = text
            elif "region" in item_id:
                address.state_province = text
            elif "country" in item_id:
                address.country = text
                address.country_code = item.get("short_code", "").upper()
                
        return address
        
    def _calculate_cost(self, operation: str) -> float:
        """Calculate Mapbox API cost"""
        # Mapbox pricing
        costs = {
            "geocoding": 0.0005,  # $0.50 per 1000 requests
            "directions": 0.005,
            "isochrone": 0.005
        }
        return costs.get(operation, 0.0005)

class GeofencingManager:
    """Manage geofencing and location-based triggers"""
    
    def __init__(self) -> None:
        self.geofences = {}  # In production, use database
        
    async def create_geofence(self, name: str, center: Coordinates, 
                            radius: float, region_type: RegionType = RegionType.CITY) -> str:
        """Create a geofence"""
        geofence_id = str(uuid.uuid4())
        
        geofence = {
            "id": geofence_id,
            "name": name,
            "center": asdict(center),
            "radius": radius,  # in meters
            "region_type": region_type.value,
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
            "triggers": [],
            "entry_count": 0,
            "exit_count": 0
        }
        
        self.geofences[geofence_id] = geofence
        return geofence_id
        
    async def check_geofence_entry(self, location: Coordinates) -> List[Dict[str, Any]]:
        """Check if location is inside any geofences"""
        entered_geofences = []
        
        for geofence_id, geofence in self.geofences.items():
            if not geofence["active"]:
                continue
                
            center = Coordinates(**geofence["center"])
            radius = geofence["radius"]
            
            distance = self._calculate_distance(location, center)
            
            if distance <= radius:
                entered_geofences.append({
                    "geofence_id": geofence_id,
                    "name": geofence["name"],
                    "distance_from_center": distance,
                    "region_type": geofence["region_type"],
                    "triggers": geofence["triggers"]
                })
                
                # Update entry count
                geofence["entry_count"] += 1
                
        return entered_geofences
        
    def _calculate_distance(self, point1: Coordinates, point2: Coordinates) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(point1.latitude)
        lon1_rad = math.radians(point1.longitude)
        lat2_rad = math.radians(point2.latitude)
        lon2_rad = math.radians(point2.longitude)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

class LocationAnalytics:
    """Analyze location patterns and insights"""
    
    def __init__(self) -> None:
        self.location_history = []
        
    async def track_location(self, user_id -> None: str, location_data -> None: LocationData, 
                           context -> None: Dict[str, Any] = None) -> None:
        """Track user location for analytics"""
        location_record = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "location_data": asdict(location_data),
            "context": context or {},
            "session_id": context.get("session_id") if context else None
        }
        
        self.location_history.append(location_record)
        
    async def get_user_location_patterns(self, user_id: str, 
                                       days: int = 30) -> Dict[str, Any]:
        """Analyze user location patterns"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        user_locations = [
            record for record in self.location_history
            if record["user_id"] == user_id and 
               datetime.fromisoformat(record["timestamp"]) >= since_date
        ]
        
        if not user_locations:
            return {"error": "No location data found"}
            
        # Analyze patterns
        countries = {}
        cities = {}
        timezones = {}
        
        for record in user_locations:
            location = record["location_data"]
            
            if location.get("address"):
                address = location["address"]
                country = address.get("country")
                city = address.get("city")
                
                if country:
                    countries[country] = countries.get(country, 0) + 1
                if city:
                    cities[city] = cities.get(city, 0) + 1
                    
            if location.get("timezone"):
                tz = location["timezone"]
                timezones[tz] = timezones.get(tz, 0) + 1
                
        return {
            "user_id": user_id,
            "analysis_period_days": days,
            "total_locations": len(user_locations),
            "countries_visited": len(countries),
            "cities_visited": len(cities),
            "most_common_country": max(countries.items(), key=lambda x: x[1])[0] if countries else None,
            "most_common_city": max(cities.items(), key=lambda x: x[1])[0] if cities else None,
            "primary_timezone": max(timezones.items(), key=lambda x: x[1])[0] if timezones else None,
            "location_distribution": {
                "countries": countries,
                "cities": cities,
                "timezones": timezones
            }
        }
        
    async def get_regional_content_insights(self, region: str, 
                                          region_type: RegionType = RegionType.COUNTRY) -> Dict[str, Any]:
        """Get content insights for a specific region"""
        region_locations = [
            record for record in self.location_history
            if self._location_matches_region(record["location_data"], region, region_type)
        ]
        
        if not region_locations:
            return {"error": f"No data found for {region}"}
            
        # Analyze engagement patterns
        total_sessions = len(set(record.get("context", {}).get("session_id") 
                               for record in region_locations 
                               if record.get("context", {}).get("session_id")))
        
        unique_users = len(set(record["user_id"] for record in region_locations))
        
        # Time pattern analysis
        hours = {}
        for record in region_locations:
            hour = datetime.fromisoformat(record["timestamp"]).hour
            hours[hour] = hours.get(hour, 0) + 1
            
        peak_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else None
        
        return {
            "region": region,
            "region_type": region_type.value,
            "total_interactions": len(region_locations),
            "unique_users": unique_users,
            "total_sessions": total_sessions,
            "peak_hour": peak_hour,
            "hourly_distribution": hours,
            "average_sessions_per_user": total_sessions / max(unique_users, 1),
            "recommendations": self._generate_regional_recommendations(region, region_type, hours)
        }
        
    def _location_matches_region(self, location_data: Dict[str, Any], 
                               region: str, region_type: RegionType) -> bool:
        """Check if location matches specified region"""
        if not location_data.get("address"):
            return False
            
        address = location_data["address"]
        
        if region_type == RegionType.COUNTRY:
            return address.get("country", "").lower() == region.lower()
        elif region_type == RegionType.CITY:
            return address.get("city", "").lower() == region.lower()
        elif region_type == RegionType.STATE_PROVINCE:
            return address.get("state_province", "").lower() == region.lower()
            
        return False
        
    def _generate_regional_recommendations(self, region: str, region_type: RegionType, 
                                        hourly_data: Dict[int, int]) -> List[str]:
        """Generate content recommendations for region"""
        recommendations = []
        
        if hourly_data:
            peak_hour = max(hourly_data.items(), key=lambda x: x[1])[0]
            
            if 6 <= peak_hour <= 9:
                recommendations.append("Consider morning-focused content for this region")
            elif 12 <= peak_hour <= 14:
                recommendations.append("Lunch-time content performs well in this region")
            elif 18 <= peak_hour <= 22:
                recommendations.append("Evening content has highest engagement")
            elif 22 <= peak_hour or peak_hour <= 6:
                recommendations.append("Late-night content strategy may be effective")
                
        recommendations.append(f"Localize content for {region} cultural preferences")
        recommendations.append("Consider regional holidays and events in content calendar")
        
        return recommendations

class GeolocationServicesManager:
    """Main manager for all geolocation services"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.providers = {}
        self.geofencing_manager = GeofencingManager()
        self.location_analytics = LocationAnalytics()
        self._initialize_providers()
        
    def _initialize_providers(self) -> None:
        """Initialize geolocation providers"""
        try:
            # Google Maps
            if google_config := self.config.get("google_maps"):
                self.providers["google_maps"] = GoogleMapsAPI(
                    api_key=google_config["api_key"]
                )
                
            # IP-API
            if ipapi_config := self.config.get("ipapi"):
                self.providers["ipapi"] = IPAPIService(
                    api_key=ipapi_config.get("api_key")
                )
            else:
                # Free version
                self.providers["ipapi"] = IPAPIService()
                
            # Mapbox
            if mapbox_config := self.config.get("mapbox"):
                self.providers["mapbox"] = MapboxAPI(
                    access_token=mapbox_config["access_token"]
                )
                
            logger.info("Geolocation providers initialized", providers=list(self.providers.keys()))
            
        except Exception as e:
            logger.error("Failed to initialize geolocation providers", error=str(e))
            
    async def geolocate(self, request: GeolocationRequest) -> GeolocationResponse:
        """Perform geolocation using optimal provider"""
        try:
            provider_name = self._choose_provider(request)
            provider = self.providers.get(provider_name)
            
            if not provider:
                return GeolocationResponse(
                    request_id=request.request_id,
                    success=False,
                    provider=GeolocationProvider(provider_name),
                    error_message=f"Provider {provider_name} not available"
                )
                
            # Route to appropriate method based on input type
            async with provider as api:
                if request.input_type == LocationType.IP_ADDRESS:
                    if hasattr(api, 'geolocate_ip'):
                        return await api.geolocate_ip(request.input_data, request)
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider(provider_name),
                            error_message="IP geolocation not supported by this provider"
                        )
                        
                elif request.input_type == LocationType.ADDRESS:
                    if hasattr(api, 'geocode_address'):
                        return await api.geocode_address(request.input_data, request)
                    elif hasattr(api, 'geocode'):
                        return await api.geocode(request.input_data, request)
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider(provider_name),
                            error_message="Address geocoding not supported by this provider"
                        )
                        
                elif request.input_type == LocationType.COORDINATES:
                    coords = self._parse_coordinates(request.input_data)
                    if coords and hasattr(api, 'reverse_geocode'):
                        return await api.reverse_geocode(coords, request)
                    else:
                        return GeolocationResponse(
                            request_id=request.request_id,
                            success=False,
                            provider=GeolocationProvider(provider_name),
                            error_message="Reverse geocoding not supported or invalid coordinates"
                        )
                        
                else:
                    return GeolocationResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=GeolocationProvider(provider_name),
                        error_message=f"Input type {request.input_type} not supported"
                    )
                    
        except Exception as e:
            logger.error("Geolocation failed", error=str(e))
            return GeolocationResponse(
                request_id=request.request_id,
                success=False,
                provider=GeolocationProvider("unknown"),
                error_message=str(e)
            )
            
    def _choose_provider(self, request: GeolocationRequest) -> str:
        """Choose optimal provider based on request type"""
        if request.provider and request.provider.value in self.providers:
            return request.provider.value
            
        # Provider selection logic
        if request.input_type == LocationType.IP_ADDRESS:
            return "ipapi" if "ipapi" in self.providers else "google_maps"
        elif request.input_type in [LocationType.ADDRESS, LocationType.COORDINATES]:
            if request.include_timezone and "google_maps" in self.providers:
                return "google_maps"
            return "mapbox" if "mapbox" in self.providers else "google_maps"
        else:
            return list(self.providers.keys())[0] if self.providers else "google_maps"
            
    def _parse_coordinates(self, coord_string: str) -> Optional[Coordinates]:
        """Parse coordinate string to Coordinates object"""
        try:
            parts = coord_string.split(",")
            if len(parts) >= 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return Coordinates(latitude=lat, longitude=lon)
        except:
            pass
        return None
        
    async def create_location_based_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create location-based content campaign"""
        campaign = {
            "campaign_id": str(uuid.uuid4()),
            "name": campaign_config.get("name"),
            "created_at": datetime.utcnow().isoformat(),
            "target_regions": campaign_config.get("target_regions", []),
            "geofences": [],
            "analytics": {
                "total_impressions": 0,
                "regional_breakdown": {},
                "engagement_by_location": {}
            }
        }
        
        # Create geofences for target regions
        for region in campaign_config.get("target_regions", []):
            if "coordinates" in region and "radius" in region:
                coords = Coordinates(**region["coordinates"])
                geofence_id = await self.geofencing_manager.create_geofence(
                    name=f"{campaign['name']} - {region.get('name', 'Region')}",
                    center=coords,
                    radius=region["radius"],
                    region_type=RegionType(region.get("type", "city"))
                )
                campaign["geofences"].append(geofence_id)
                
        return campaign
        
    async def get_location_insights(self, user_id: str = None, 
                                  region: str = None) -> Dict[str, Any]:
        """Get comprehensive location insights"""
        insights = {
            "generated_at": datetime.utcnow().isoformat(),
            "insights_type": "user" if user_id else "regional"
        }
        
        if user_id:
            insights["user_patterns"] = await self.location_analytics.get_user_location_patterns(user_id)
        
        if region:
            insights["regional_insights"] = await self.location_analytics.get_regional_content_insights(region)
            
        return insights

# Factory function for easy integration
def create_geolocation_manager(config: Dict[str, Any]) -> GeolocationServicesManager:
    """Create configured geolocation manager"""
    return GeolocationServicesManager(config)

# Example usage for Ainflue platform
async def ainflue_location_intelligence_workflow(user_ip: str, content_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete location intelligence workflow for Ainflue creators
    Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
    """
    
    # Example configuration
    config = {
        "google_maps": {
            "api_key": "your_google_maps_api_key"
        },
        "ipapi": {
            "api_key": "your_ipapi_key"  # Optional for pro features
        },
        "mapbox": {
            "access_token": "your_mapbox_access_token"
        }
    }
    
    # Initialize geolocation manager
    geo_manager = create_geolocation_manager(config)
    
    # Geolocate user by IP
    ip_request = GeolocationRequest(
        input_data=user_ip,
        input_type=LocationType.IP_ADDRESS,
        include_timezone=True,
        include_currency=True,
        include_security=True
    )
    
    location_result = await geo_manager.geolocate(ip_request)
    
    # Create location-based campaign targeting
    if location_result.success and location_result.location_data:
        location_data = location_result.location_data
        
        # Create targeted campaign
        campaign_config = {
            "name": f"Ainflue Regional Campaign - {location_data.address.country if location_data.address else 'Unknown'}",
            "target_regions": [
                {
                    "name": location_data.address.city if location_data.address else "Unknown City",
                    "coordinates": {
                        "latitude": location_data.coordinates.latitude,
                        "longitude": location_data.coordinates.longitude
                    } if location_data.coordinates else None,
                    "radius": 50000,  # 50km radius
                    "type": "city"
                }
            ]
        }
        
        campaign = await geo_manager.create_location_based_campaign(campaign_config)
        
        # Get regional insights
        if location_data.address and location_data.address.country:
            regional_insights = await geo_manager.get_location_insights(
                region=location_data.address.country
            )
        else:
            regional_insights = {"error": "Insufficient location data for regional insights"}
            
    else:
        campaign = {"error": "Could not create campaign without location data"}
        regional_insights = {"error": "Could not get regional insights without location data"}
        
    return {
        "user_location": location_result.dict() if hasattr(location_result, 'dict') else asdict(location_result),
        "location_based_campaign": campaign,
        "regional_insights": regional_insights,
        "content_recommendations": [
            "Localize content language based on detected region",
            "Consider local time zones for optimal posting schedules",
            "Adapt monetization strategies to regional preferences",
            "Include region-specific cultural references when appropriate",
            "Comply with local data protection and content regulations"
        ],
        "monetization_insights": {
            "currency": location_data.currency if location_result.success and location_result.location_data else "USD",
            "suggested_payment_methods": ["Credit Card", "PayPal", "Local Bank Transfer"],
            "regional_pricing_factor": 1.0,  # Adjust based on regional purchasing power
            "tax_considerations": "Consult local tax regulations for content monetization"
        }
    }

if __name__ == "__main__":
    # Test the geolocation services integration
    import asyncio
    
    async def test_geolocation_services() -> None:
        """Test geolocation services functionality"""
        
        test_ip = "8.8.8.8"  # Google DNS for testing
        test_preferences = {
            "content_type": "video",
            "preferred_language": "en",
            "monetization_enabled": True
        }
        
        result = await ainflue_location_intelligence_workflow(test_ip, test_preferences)
        
        print("Location Intelligence Workflow Result:")
        print(json.dumps(result, indent=2, default=str))
        
    # Run test
    # asyncio.run(test_geolocation_services())
    
    print("✅ Geolocation Services Integration Module loaded successfully")
    print("🌍 Enterprise-grade location intelligence for Ainflue creators")
    print("📍 IP geolocation, address geocoding, geofencing, and location analytics ready")