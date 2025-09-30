#!/usr/bin/env python3
"""
Ainflue Platform - Weather Services Integration Module
Enterprise-grade weather APIs for contextual content creation and targeting

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Integration-Level: Level 3 (integrations/third_party/)
Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
Weather Context: Seasonal content, weather-based targeting, atmospheric content optimization
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

# Configure structured logging
logger = structlog.get_logger(__name__)

class WeatherProvider(str, Enum):
    """Supported weather providers"""
    OPENWEATHERMAP = "openweathermap"
    WEATHERAPI = "weatherapi"
    ACCUWEATHER = "accuweather"
    DARKSKY = "darksky"  # Apple Weather
    VISUALCROSSING = "visualcrossing"
    CLIMACELL = "climacell"  # Tomorrow.io
    WEATHERBIT = "weatherbit"
    METEOSTAT = "meteostat"

class WeatherCondition(str, Enum):
    """Weather condition categories"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    SNOW = "snow"
    SLEET = "sleet"
    FOG = "fog"
    MIST = "mist"
    THUNDERSTORM = "thunderstorm"
    HAIL = "hail"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    SANDSTORM = "sandstorm"

class ForecastType(str, Enum):
    """Types of weather forecasts"""
    CURRENT = "current"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    HISTORICAL = "historical"
    ALERTS = "alerts"

@dataclass
class WeatherData:
    """Current weather data structure"""
    temperature: float  # in Celsius
    temperature_feels_like: float
    humidity: int  # percentage
    pressure: float  # in hPa
    visibility: Optional[float] = None  # in km
    uv_index: Optional[float] = None
    wind_speed: float = 0.0  # in km/h
    wind_direction: Optional[int] = None  # in degrees
    wind_gust: Optional[float] = None  # in km/h
    precipitation: float = 0.0  # in mm
    condition: WeatherCondition = WeatherCondition.CLEAR
    condition_text: str = ""
    cloud_cover: int = 0  # percentage
    dewpoint: Optional[float] = None
    air_quality_index: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ForecastItem:
    """Weather forecast item"""
    date: datetime
    temperature_max: float
    temperature_min: float
    condition: WeatherCondition
    condition_text: str
    precipitation_probability: int = 0  # percentage
    precipitation_amount: float = 0.0  # in mm
    wind_speed: float = 0.0
    humidity: int = 0
    uv_index: Optional[float] = None

@dataclass
class WeatherAlert:
    """Weather alert/warning"""
    alert_id: str
    title: str
    description: str
    severity: str  # "minor", "moderate", "severe", "extreme"
    urgency: str  # "immediate", "expected", "future", "past"
    certainty: str  # "observed", "likely", "possible", "unlikely"
    areas: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source: str = ""

class WeatherRequest(BaseModel):
    """Weather request structure"""
    location: str  # coordinates, city name, or postal code
    forecast_type: ForecastType = ForecastType.CURRENT
    days: int = 1  # for daily forecasts
    hours: int = 24  # for hourly forecasts
    include_alerts: bool = False
    include_air_quality: bool = False
    include_astronomy: bool = False
    units: str = "metric"  # metric, imperial
    language: str = "en"
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WeatherResponse(BaseModel):
    """Weather response structure"""
    request_id: str
    success: bool = True
    location: str = ""
    coordinates: Optional[Dict[str, float]] = None
    current_weather: Optional[WeatherData] = None
    forecast: List[ForecastItem] = Field(default_factory=list)
    alerts: List[WeatherAlert] = Field(default_factory=list)
    air_quality: Optional[Dict[str, Any]] = None
    astronomy: Optional[Dict[str, Any]] = None
    provider: WeatherProvider
    processing_time: float = 0.0
    cost: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OpenWeatherMapAPI:
    """OpenWeatherMap API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        """Get weather data from OpenWeatherMap"""
        try:
            start_time = time.time()
            
            # First, get coordinates if location is not coordinates
            coordinates = await self._get_coordinates(request.location)
            if not coordinates:
                return WeatherResponse(
                    request_id=request.request_id,
                    success=False,
                    provider=WeatherProvider.OPENWEATHERMAP,
                    error_message="Could not resolve location coordinates"
                )
                
            # Use One Call API for comprehensive data
            params = {
                "lat": coordinates["lat"],
                "lon": coordinates["lon"],
                "appid": self.api_key,
                "units": request.units,
                "lang": request.language
            }
            
            if request.forecast_type != ForecastType.CURRENT:
                params["exclude"] = "minutely"
            else:
                params["exclude"] = "minutely,hourly,daily,alerts"
                
            async with self.session.get(self.onecall_url, params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse current weather
                    current_weather = None
                    if "current" in data:
                        current_weather = self._parse_current_weather(data["current"])
                        
                    # Parse forecast
                    forecast = []
                    if request.forecast_type == ForecastType.DAILY and "daily" in data:
                        forecast = self._parse_daily_forecast(data["daily"][:request.days])
                    elif request.forecast_type == ForecastType.HOURLY and "hourly" in data:
                        forecast = self._parse_hourly_forecast(data["hourly"][:request.hours])
                        
                    # Parse alerts
                    alerts = []
                    if request.include_alerts and "alerts" in data:
                        alerts = self._parse_alerts(data["alerts"])
                        
                    return WeatherResponse(
                        request_id=request.request_id,
                        success=True,
                        location=request.location,
                        coordinates=coordinates,
                        current_weather=current_weather,
                        forecast=forecast,
                        alerts=alerts,
                        provider=WeatherProvider.OPENWEATHERMAP,
                        processing_time=processing_time,
                        cost=self._calculate_cost(request.forecast_type)
                    )
                else:
                    error_data = await response.json()
                    return WeatherResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=WeatherProvider.OPENWEATHERMAP,
                        error_message=error_data.get("message", f"API error: {response.status}")
                    )
                    
        except Exception as e:
            logger.error("OpenWeatherMap API failed", error=str(e))
            return WeatherResponse(
                request_id=request.request_id,
                success=False,
                provider=WeatherProvider.OPENWEATHERMAP,
                error_message=str(e)
            )
            
    async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for location using geocoding API"""
        try:
            # Check if location is already coordinates
            if "," in location:
                parts = location.split(",")
                if len(parts) == 2:
                    try:
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                        return {"lat": lat, "lon": lon}
                    except ValueError:
                        pass
                        
            # Use geocoding API
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            async with self.session.get("http://api.openweathermap.org/geo/1.0/direct", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
                        
            return None
            
        except Exception as e:
            logger.error("Geocoding failed", error=str(e))
            return None
            
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherData:
        """Parse current weather data"""
        weather = data["weather"][0]
        
        return WeatherData(
            temperature=data["temp"],
            temperature_feels_like=data["feels_like"],
            humidity=data["humidity"],
            pressure=data["pressure"],
            visibility=data.get("visibility", 0) / 1000,  # Convert m to km
            uv_index=data.get("uvi"),
            wind_speed=data.get("wind_speed", 0) * 3.6,  # Convert m/s to km/h
            wind_direction=data.get("wind_deg"),
            wind_gust=data.get("wind_gust", 0) * 3.6 if data.get("wind_gust") else None,
            condition=self._map_condition(weather["id"]),
            condition_text=weather["description"],
            cloud_cover=data.get("clouds", 0),
            dewpoint=data.get("dew_point"),
            timestamp=datetime.fromtimestamp(data["dt"])
        )
        
    def _parse_daily_forecast(self, daily_data: List[Dict[str, Any]]) -> List[ForecastItem]:
        """Parse daily forecast data"""
        forecast = []
        
        for day in daily_data:
            weather = day["weather"][0]
            
            item = ForecastItem(
                date=datetime.fromtimestamp(day["dt"]),
                temperature_max=day["temp"]["max"],
                temperature_min=day["temp"]["min"],
                condition=self._map_condition(weather["id"]),
                condition_text=weather["description"],
                precipitation_probability=int(day.get("pop", 0) * 100),
                precipitation_amount=day.get("rain", {}).get("1h", 0) + day.get("snow", {}).get("1h", 0),
                wind_speed=day.get("wind_speed", 0) * 3.6,
                humidity=day.get("humidity", 0),
                uv_index=day.get("uvi")
            )
            forecast.append(item)
            
        return forecast
        
    def _parse_hourly_forecast(self, hourly_data: List[Dict[str, Any]]) -> List[ForecastItem]:
        """Parse hourly forecast data"""
        forecast = []
        
        for hour in hourly_data:
            weather = hour["weather"][0]
            
            item = ForecastItem(
                date=datetime.fromtimestamp(hour["dt"]),
                temperature_max=hour["temp"],
                temperature_min=hour["temp"],
                condition=self._map_condition(weather["id"]),
                condition_text=weather["description"],
                precipitation_probability=int(hour.get("pop", 0) * 100),
                precipitation_amount=hour.get("rain", {}).get("1h", 0) + hour.get("snow", {}).get("1h", 0),
                wind_speed=hour.get("wind_speed", 0) * 3.6,
                humidity=hour.get("humidity", 0),
                uv_index=hour.get("uvi")
            )
            forecast.append(item)
            
        return forecast
        
    def _parse_alerts(self, alerts_data: List[Dict[str, Any]]) -> List[WeatherAlert]:
        """Parse weather alerts"""
        alerts = []
        
        for alert in alerts_data:
            weather_alert = WeatherAlert(
                alert_id=str(uuid.uuid4()),
                title=alert.get("event", "Weather Alert"),
                description=alert.get("description", ""),
                severity="moderate",  # OpenWeatherMap doesn't provide severity levels
                urgency="immediate",
                certainty="likely",
                source=alert.get("sender_name", "OpenWeatherMap"),
                start_time=datetime.fromtimestamp(alert["start"]) if "start" in alert else None,
                end_time=datetime.fromtimestamp(alert["end"]) if "end" in alert else None
            )
            alerts.append(weather_alert)
            
        return alerts
        
    def _map_condition(self, condition_id: int) -> WeatherCondition:
        """Map OpenWeatherMap condition ID to WeatherCondition enum"""
        condition_mapping = {
            # Clear
            800: WeatherCondition.CLEAR,
            # Clouds
            801: WeatherCondition.PARTLY_CLOUDY,
            802: WeatherCondition.PARTLY_CLOUDY,
            803: WeatherCondition.CLOUDY,
            804: WeatherCondition.OVERCAST,
            # Rain
            500: WeatherCondition.DRIZZLE,
            501: WeatherCondition.RAIN,
            502: WeatherCondition.RAIN,
            503: WeatherCondition.RAIN,
            504: WeatherCondition.RAIN,
            511: WeatherCondition.SLEET,
            520: WeatherCondition.RAIN,
            521: WeatherCondition.RAIN,
            522: WeatherCondition.RAIN,
            531: WeatherCondition.RAIN,
            # Drizzle
            300: WeatherCondition.DRIZZLE,
            301: WeatherCondition.DRIZZLE,
            302: WeatherCondition.DRIZZLE,
            310: WeatherCondition.DRIZZLE,
            311: WeatherCondition.DRIZZLE,
            312: WeatherCondition.DRIZZLE,
            313: WeatherCondition.DRIZZLE,
            314: WeatherCondition.DRIZZLE,
            321: WeatherCondition.DRIZZLE,
            # Thunderstorm
            200: WeatherCondition.THUNDERSTORM,
            201: WeatherCondition.THUNDERSTORM,
            202: WeatherCondition.THUNDERSTORM,
            210: WeatherCondition.THUNDERSTORM,
            211: WeatherCondition.THUNDERSTORM,
            212: WeatherCondition.THUNDERSTORM,
            221: WeatherCondition.THUNDERSTORM,
            230: WeatherCondition.THUNDERSTORM,
            231: WeatherCondition.THUNDERSTORM,
            232: WeatherCondition.THUNDERSTORM,
            # Snow
            600: WeatherCondition.SNOW,
            601: WeatherCondition.SNOW,
            602: WeatherCondition.SNOW,
            611: WeatherCondition.SLEET,
            612: WeatherCondition.SLEET,
            613: WeatherCondition.SLEET,
            615: WeatherCondition.SNOW,
            616: WeatherCondition.SNOW,
            620: WeatherCondition.SNOW,
            621: WeatherCondition.SNOW,
            622: WeatherCondition.SNOW,
            # Atmosphere
            701: WeatherCondition.MIST,
            711: WeatherCondition.FOG,
            721: WeatherCondition.FOG,
            731: WeatherCondition.SANDSTORM,
            741: WeatherCondition.FOG,
            751: WeatherCondition.SANDSTORM,
            761: WeatherCondition.SANDSTORM,
            762: WeatherCondition.SANDSTORM,
            771: WeatherCondition.TORNADO,
            781: WeatherCondition.TORNADO
        }
        
        return condition_mapping.get(condition_id, WeatherCondition.CLEAR)
        
    def _calculate_cost(self, forecast_type: ForecastType) -> float:
        """Calculate OpenWeatherMap API cost"""
        # OpenWeatherMap pricing (simplified)
        if forecast_type == ForecastType.CURRENT:
            return 0.0  # Free tier
        else:
            return 0.001  # $1 per 1000 calls

class WeatherAPIService:
    """WeatherAPI.com integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        """Get weather data from WeatherAPI"""
        try:
            start_time = time.time()
            
            # Choose endpoint based on forecast type
            if request.forecast_type == ForecastType.CURRENT:
                endpoint = "current.json"
            elif request.forecast_type in [ForecastType.DAILY, ForecastType.HOURLY]:
                endpoint = "forecast.json"
            elif request.forecast_type == ForecastType.HISTORICAL:
                endpoint = "history.json"
            else:
                endpoint = "current.json"
                
            params = {
                "key": self.api_key,
                "q": request.location,
                "lang": request.language
            }
            
            if request.forecast_type in [ForecastType.DAILY, ForecastType.HOURLY]:
                params["days"] = min(request.days, 10)  # Max 10 days
                params["aqi"] = "yes" if request.include_air_quality else "no"
                params["alerts"] = "yes" if request.include_alerts else "no"
                
            async with self.session.get(f"{self.base_url}/{endpoint}", params=params) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse location
                    location_info = data.get("location", {})
                    coordinates = {
                        "lat": location_info.get("lat"),
                        "lon": location_info.get("lon")
                    }
                    
                    # Parse current weather
                    current_weather = None
                    if "current" in data:
                        current_weather = self._parse_current_weather(data["current"])
                        
                    # Parse forecast
                    forecast = []
                    if "forecast" in data and data["forecast"]["forecastday"]:
                        if request.forecast_type == ForecastType.DAILY:
                            forecast = self._parse_daily_forecast(data["forecast"]["forecastday"])
                        elif request.forecast_type == ForecastType.HOURLY:
                            forecast = self._parse_hourly_forecast(data["forecast"]["forecastday"])
                            
                    # Parse alerts
                    alerts = []
                    if "alerts" in data and data["alerts"]["alert"]:
                        alerts = self._parse_alerts(data["alerts"]["alert"])
                        
                    # Parse air quality
                    air_quality = None
                    if request.include_air_quality and "current" in data and "air_quality" in data["current"]:
                        air_quality = data["current"]["air_quality"]
                        
                    return WeatherResponse(
                        request_id=request.request_id,
                        success=True,
                        location=f"{location_info.get('name', '')}, {location_info.get('country', '')}",
                        coordinates=coordinates,
                        current_weather=current_weather,
                        forecast=forecast,
                        alerts=alerts,
                        air_quality=air_quality,
                        provider=WeatherProvider.WEATHERAPI,
                        processing_time=processing_time,
                        cost=self._calculate_cost(request.forecast_type)
                    )
                else:
                    error_data = await response.json()
                    return WeatherResponse(
                        request_id=request.request_id,
                        success=False,
                        provider=WeatherProvider.WEATHERAPI,
                        error_message=error_data.get("error", {}).get("message", f"API error: {response.status}")
                    )
                    
        except Exception as e:
            logger.error("WeatherAPI service failed", error=str(e))
            return WeatherResponse(
                request_id=request.request_id,
                success=False,
                provider=WeatherProvider.WEATHERAPI,
                error_message=str(e)
            )
            
    def _parse_current_weather(self, data: Dict[str, Any]) -> WeatherData:
        """Parse current weather data from WeatherAPI"""
        condition = data.get("condition", {})
        
        return WeatherData(
            temperature=data.get("temp_c", 0),
            temperature_feels_like=data.get("feelslike_c", 0),
            humidity=data.get("humidity", 0),
            pressure=data.get("pressure_mb", 0),
            visibility=data.get("vis_km", 0),
            uv_index=data.get("uv", 0),
            wind_speed=data.get("wind_kph", 0),
            wind_direction=data.get("wind_degree"),
            wind_gust=data.get("gust_kph"),
            precipitation=data.get("precip_mm", 0),
            condition=self._map_condition(condition.get("text", "")),
            condition_text=condition.get("text", ""),
            cloud_cover=data.get("cloud", 0),
            timestamp=datetime.utcnow()
        )
        
    def _parse_daily_forecast(self, forecast_days: List[Dict[str, Any]]) -> List[ForecastItem]:
        """Parse daily forecast from WeatherAPI"""
        forecast = []
        
        for day in forecast_days:
            day_data = day.get("day", {})
            condition = day_data.get("condition", {})
            
            item = ForecastItem(
                date=datetime.fromisoformat(day["date"]),
                temperature_max=day_data.get("maxtemp_c", 0),
                temperature_min=day_data.get("mintemp_c", 0),
                condition=self._map_condition(condition.get("text", "")),
                condition_text=condition.get("text", ""),
                precipitation_probability=day_data.get("daily_chance_of_rain", 0),
                precipitation_amount=day_data.get("totalprecip_mm", 0),
                wind_speed=day_data.get("maxwind_kph", 0),
                humidity=day_data.get("avghumidity", 0),
                uv_index=day_data.get("uv", 0)
            )
            forecast.append(item)
            
        return forecast
        
    def _parse_hourly_forecast(self, forecast_days: List[Dict[str, Any]]) -> List[ForecastItem]:
        """Parse hourly forecast from WeatherAPI"""
        forecast = []
        
        for day in forecast_days:
            for hour in day.get("hour", []):
                condition = hour.get("condition", {})
                
                item = ForecastItem(
                    date=datetime.fromisoformat(hour["time"]),
                    temperature_max=hour.get("temp_c", 0),
                    temperature_min=hour.get("temp_c", 0),
                    condition=self._map_condition(condition.get("text", "")),
                    condition_text=condition.get("text", ""),
                    precipitation_probability=hour.get("chance_of_rain", 0),
                    precipitation_amount=hour.get("precip_mm", 0),
                    wind_speed=hour.get("wind_kph", 0),
                    humidity=hour.get("humidity", 0),
                    uv_index=hour.get("uv", 0)
                )
                forecast.append(item)
                
        return forecast
        
    def _parse_alerts(self, alerts_data: List[Dict[str, Any]]) -> List[WeatherAlert]:
        """Parse weather alerts from WeatherAPI"""
        alerts = []
        
        for alert in alerts_data:
            weather_alert = WeatherAlert(
                alert_id=str(uuid.uuid4()),
                title=alert.get("headline", "Weather Alert"),
                description=alert.get("desc", ""),
                severity=alert.get("severity", "moderate").lower(),
                urgency=alert.get("urgency", "expected").lower(),
                certainty=alert.get("certainty", "likely").lower(),
                areas=alert.get("areas", []),
                source="WeatherAPI"
            )
            alerts.append(weather_alert)
            
        return alerts
        
    def _map_condition(self, condition_text: str) -> WeatherCondition:
        """Map WeatherAPI condition text to WeatherCondition enum"""
        condition_text = condition_text.lower()
        
        if "clear" in condition_text or "sunny" in condition_text:
            return WeatherCondition.CLEAR
        elif "partly cloudy" in condition_text:
            return WeatherCondition.PARTLY_CLOUDY
        elif "cloudy" in condition_text or "overcast" in condition_text:
            return WeatherCondition.CLOUDY
        elif "rain" in condition_text or "shower" in condition_text:
            return WeatherCondition.RAIN
        elif "drizzle" in condition_text:
            return WeatherCondition.DRIZZLE
        elif "snow" in condition_text or "blizzard" in condition_text:
            return WeatherCondition.SNOW
        elif "sleet" in condition_text:
            return WeatherCondition.SLEET
        elif "fog" in condition_text:
            return WeatherCondition.FOG
        elif "mist" in condition_text:
            return WeatherCondition.MIST
        elif "thunder" in condition_text:
            return WeatherCondition.THUNDERSTORM
        elif "hail" in condition_text:
            return WeatherCondition.HAIL
        else:
            return WeatherCondition.CLEAR
            
    def _calculate_cost(self, forecast_type: ForecastType) -> float:
        """Calculate WeatherAPI cost"""
        # WeatherAPI pricing
        return 0.0  # Free tier up to 1M calls/month

class WeatherContentOptimizer:
    """Optimize content based on weather conditions"""
    
    def __init__(self):
        self.weather_content_mapping = {
            WeatherCondition.CLEAR: {
                "mood": "bright and energetic",
                "colors": ["yellow", "orange", "bright blue"],
                "activities": ["outdoor", "sports", "travel", "photography"],
                "keywords": ["sunshine", "bright", "outdoor", "adventure"]
            },
            WeatherCondition.RAIN: {
                "mood": "cozy and introspective",
                "colors": ["blue", "gray", "dark green"],
                "activities": ["indoor", "reading", "cooking", "crafts"],
                "keywords": ["cozy", "indoor", "comfort", "relaxation"]
            },
            WeatherCondition.SNOW: {
                "mood": "magical and serene",
                "colors": ["white", "silver", "light blue"],
                "activities": ["winter sports", "hot drinks", "fireplace"],
                "keywords": ["winter", "magical", "serene", "peaceful"]
            },
            WeatherCondition.CLOUDY: {
                "mood": "contemplative and calm",
                "colors": ["gray", "muted blue", "soft white"],
                "activities": ["reading", "thinking", "planning"],
                "keywords": ["thoughtful", "calm", "reflective", "peaceful"]
            },
            WeatherCondition.THUNDERSTORM: {
                "mood": "dramatic and powerful",
                "colors": ["dark gray", "purple", "yellow"],
                "activities": ["indoor entertainment", "dramatic content"],
                "keywords": ["dramatic", "powerful", "intense", "energy"]
            }
        }
        
    async def optimize_content_for_weather(self, weather_data: WeatherData, 
                                         content_type: str = "general") -> Dict[str, Any]:
        """Generate weather-optimized content recommendations"""
        condition = weather_data.condition
        temperature = weather_data.temperature
        
        # Get base recommendations for weather condition
        base_recommendations = self.weather_content_mapping.get(condition, {})
        
        # Temperature-based adjustments
        temperature_factor = self._get_temperature_factor(temperature)
        
        # Generate content optimization
        optimization = {
            "weather_condition": condition.value,
            "temperature": temperature,
            "temperature_factor": temperature_factor,
            "mood_recommendation": base_recommendations.get("mood", "neutral"),
            "color_palette": base_recommendations.get("colors", ["neutral"]),
            "activity_themes": base_recommendations.get("activities", ["general"]),
            "content_keywords": base_recommendations.get("keywords", ["weather"]),
            "posting_recommendations": self._get_posting_recommendations(weather_data),
            "engagement_predictions": self._predict_engagement(weather_data),
            "seasonal_adjustments": self._get_seasonal_adjustments(weather_data)
        }
        
        # Content type specific optimizations
        if content_type == "video":
            optimization["video_recommendations"] = self._get_video_recommendations(weather_data)
        elif content_type == "photo":
            optimization["photo_recommendations"] = self._get_photo_recommendations(weather_data)
        elif content_type == "text":
            optimization["text_recommendations"] = self._get_text_recommendations(weather_data)
            
        return optimization
        
    def _get_temperature_factor(self, temperature: float) -> str:
        """Get temperature factor for content optimization"""
        if temperature < 0:
            return "very_cold"
        elif temperature < 10:
            return "cold"
        elif temperature < 20:
            return "cool"
        elif temperature < 30:
            return "warm"
        else:
            return "hot"
            
    def _get_posting_recommendations(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Get posting time recommendations based on weather"""
        recommendations = {
            "optimal_times": [],
            "avoid_times": [],
            "frequency_adjustment": 1.0,
            "engagement_multiplier": 1.0
        }
        
        # Weather-based timing
        if weather_data.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW]:
            recommendations["optimal_times"] = ["morning", "evening"]
            recommendations["engagement_multiplier"] = 1.2  # People more likely to be indoors
        elif weather_data.condition == WeatherCondition.CLEAR:
            recommendations["optimal_times"] = ["early_morning", "late_evening"]
            recommendations["avoid_times"] = ["afternoon"]  # People likely outdoors
            recommendations["engagement_multiplier"] = 0.8
            
        return recommendations
        
    def _predict_engagement(self, weather_data: WeatherData) -> Dict[str, float]:
        """Predict engagement levels based on weather"""
        base_engagement = 1.0
        
        # Weather condition effects
        condition_multipliers = {
            WeatherCondition.RAIN: 1.3,
            WeatherCondition.SNOW: 1.4,
            WeatherCondition.THUNDERSTORM: 1.2,
            WeatherCondition.CLEAR: 0.8,
            WeatherCondition.CLOUDY: 1.1
        }
        
        engagement_multiplier = condition_multipliers.get(weather_data.condition, 1.0)
        
        # Temperature effects
        if weather_data.temperature < 5 or weather_data.temperature > 35:
            engagement_multiplier *= 1.2  # Extreme temperatures keep people indoors
            
        return {
            "predicted_engagement": base_engagement * engagement_multiplier,
            "confidence": 0.75,
            "factors": {
                "weather_condition": weather_data.condition.value,
                "temperature_effect": weather_data.temperature,
                "overall_multiplier": engagement_multiplier
            }
        }
        
    def _get_seasonal_adjustments(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Get seasonal content adjustments"""
        current_month = datetime.now().month
        
        seasonal_themes = {
            12: "winter_holidays",
            1: "new_year",
            2: "winter",
            3: "spring_beginning",
            4: "spring",
            5: "spring_end",
            6: "summer_beginning",
            7: "summer",
            8: "summer_end",
            9: "autumn_beginning",
            10: "autumn",
            11: "pre_winter"
        }
        
        return {
            "current_season": seasonal_themes.get(current_month, "general"),
            "seasonal_keywords": self._get_seasonal_keywords(current_month),
            "holiday_considerations": self._get_holiday_considerations(current_month)
        }
        
    def _get_seasonal_keywords(self, month: int) -> List[str]:
        """Get seasonal keywords for content"""
        keyword_mapping = {
            12: ["holiday", "winter", "celebration", "year-end"],
            1: ["new year", "fresh start", "resolution", "winter"],
            2: ["valentine", "love", "winter", "indoor"],
            3: ["spring", "renewal", "growth", "fresh"],
            4: ["easter", "spring", "outdoor", "nature"],
            5: ["mother's day", "spring", "flowers", "outdoor"],
            6: ["summer", "vacation", "outdoor", "travel"],
            7: ["summer", "vacation", "beach", "sun"],
            8: ["summer", "back to school", "transition"],
            9: ["autumn", "back to school", "harvest"],
            10: ["halloween", "autumn", "cozy", "seasonal"],
            11: ["thanksgiving", "gratitude", "autumn", "family"]
        }
        
        return keyword_mapping.get(month, ["general"])
        
    def _get_holiday_considerations(self, month: int) -> List[str]:
        """Get holiday considerations for content"""
        holiday_mapping = {
            12: ["Christmas", "New Year's Eve", "Hanukkah"],
            1: ["New Year's Day", "Martin Luther King Jr. Day"],
            2: ["Valentine's Day", "Presidents' Day"],
            3: ["St. Patrick's Day", "Easter (varies)"],
            4: ["Easter (varies)", "Earth Day"],
            5: ["Mother's Day", "Memorial Day"],
            6: ["Father's Day", "Summer Solstice"],
            7: ["Independence Day (US)", "Summer holidays"],
            8: ["Back to school season"],
            9: ["Labor Day", "Autumn Equinox"],
            10: ["Halloween", "Columbus Day"],
            11: ["Thanksgiving", "Veterans Day"]
        }
        
        return holiday_mapping.get(month, [])
        
    def _get_video_recommendations(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Get video-specific recommendations"""
        return {
            "lighting": "natural" if weather_data.condition == WeatherCondition.CLEAR else "artificial",
            "indoor_vs_outdoor": "indoor" if weather_data.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW] else "outdoor",
            "duration": "longer" if weather_data.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW] else "shorter",
            "style": "cozy" if weather_data.condition == WeatherCondition.RAIN else "energetic"
        }
        
    def _get_photo_recommendations(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Get photo-specific recommendations"""
        return {
            "filter_style": "warm" if weather_data.temperature > 20 else "cool",
            "composition": "close-up" if weather_data.condition in [WeatherCondition.RAIN, WeatherCondition.FOG] else "wide",
            "subjects": ["indoor scenes", "cozy spaces"] if weather_data.condition == WeatherCondition.RAIN else ["landscapes", "outdoor activities"]
        }
        
    def _get_text_recommendations(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Get text content recommendations"""
        return {
            "tone": "contemplative" if weather_data.condition == WeatherCondition.RAIN else "upbeat",
            "length": "longer" if weather_data.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW] else "shorter",
            "topics": ["introspection", "indoor activities"] if weather_data.condition == WeatherCondition.RAIN else ["adventure", "outdoor activities"]
        }

class WeatherServicesManager:
    """Main manager for all weather services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {}
        self.content_optimizer = WeatherContentOptimizer()
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Initialize weather providers"""
        try:
            # OpenWeatherMap
            if openweather_config := self.config.get("openweathermap"):
                self.providers["openweathermap"] = OpenWeatherMapAPI(
                    api_key=openweather_config["api_key"]
                )
                
            # WeatherAPI
            if weatherapi_config := self.config.get("weatherapi"):
                self.providers["weatherapi"] = WeatherAPIService(
                    api_key=weatherapi_config["api_key"]
                )
                
            logger.info("Weather providers initialized", providers=list(self.providers.keys()))
            
        except Exception as e:
            logger.error("Failed to initialize weather providers", error=str(e))
            
    async def get_weather(self, request: WeatherRequest, 
                         preferred_provider: Optional[str] = None) -> WeatherResponse:
        """Get weather data using optimal provider"""
        try:
            provider_name = self._choose_provider(request, preferred_provider)
            provider = self.providers.get(provider_name)
            
            if not provider:
                return WeatherResponse(
                    request_id=request.request_id,
                    success=False,
                    provider=WeatherProvider(provider_name),
                    error_message=f"Provider {provider_name} not available"
                )
                
            async with provider as api:
                return await api.get_weather(request)
                
        except Exception as e:
            logger.error("Weather request failed", error=str(e))
            return WeatherResponse(
                request_id=request.request_id,
                success=False,
                provider=WeatherProvider("unknown"),
                error_message=str(e)
            )
            
    def _choose_provider(self, request: WeatherRequest, preferred: Optional[str] = None) -> str:
        """Choose optimal provider based on request"""
        if preferred and preferred in self.providers:
            return preferred
            
        # Provider selection logic
        if request.include_alerts and "weatherapi" in self.providers:
            return "weatherapi"  # Better alerts support
        elif request.include_air_quality and "weatherapi" in self.providers:
            return "weatherapi"  # Better air quality data
        elif "openweathermap" in self.providers:
            return "openweathermap"  # Default
        else:
            return list(self.providers.keys())[0] if self.providers else "openweathermap"
            
    async def get_weather_content_optimization(self, location: str, 
                                             content_type: str = "general") -> Dict[str, Any]:
        """Get weather-based content optimization recommendations"""
        try:
            # Get current weather
            weather_request = WeatherRequest(
                location=location,
                forecast_type=ForecastType.CURRENT,
                include_alerts=True
            )
            
            weather_response = await self.get_weather(weather_request)
            
            if not weather_response.success or not weather_response.current_weather:
                return {"error": "Could not get weather data for optimization"}
                
            # Generate content optimization
            optimization = await self.content_optimizer.optimize_content_for_weather(
                weather_response.current_weather, content_type
            )
            
            # Add weather context
            optimization["weather_context"] = {
                "location": weather_response.location,
                "current_weather": asdict(weather_response.current_weather),
                "alerts": [asdict(alert) for alert in weather_response.alerts]
            }
            
            return optimization
            
        except Exception as e:
            logger.error("Weather content optimization failed", error=str(e))
            return {"error": str(e)}
            
    async def get_location_weather_insights(self, locations: List[str], 
                                          days: int = 7) -> Dict[str, Any]:
        """Get weather insights for multiple locations"""
        insights = {
            "analysis_date": datetime.utcnow().isoformat(),
            "forecast_days": days,
            "locations": {},
            "comparative_analysis": {},
            "content_recommendations": []
        }
        
        location_weather = {}
        
        # Get weather for all locations
        for location in locations:
            try:
                weather_request = WeatherRequest(
                    location=location,
                    forecast_type=ForecastType.DAILY,
                    days=days,
                    include_alerts=True
                )
                
                weather_response = await self.get_weather(weather_request)
                
                if weather_response.success:
                    location_weather[location] = weather_response
                    insights["locations"][location] = {
                        "current_weather": asdict(weather_response.current_weather) if weather_response.current_weather else None,
                        "forecast_summary": self._summarize_forecast(weather_response.forecast),
                        "alerts_count": len(weather_response.alerts),
                        "content_potential": self._assess_content_potential(weather_response)
                    }
                    
            except Exception as e:
                logger.error(f"Weather analysis failed for {location}", error=str(e))
                insights["locations"][location] = {"error": str(e)}
                
        # Comparative analysis
        if len(location_weather) > 1:
            insights["comparative_analysis"] = self._compare_locations_weather(location_weather)
            
        # Generate content recommendations
        insights["content_recommendations"] = self._generate_multi_location_recommendations(location_weather)
        
        return insights
        
    def _summarize_forecast(self, forecast: List[ForecastItem]) -> Dict[str, Any]:
        """Summarize weather forecast"""
        if not forecast:
            return {}
            
        conditions = [item.condition for item in forecast]
        temperatures = [item.temperature_max for item in forecast]
        precipitation = [item.precipitation_probability for item in forecast]
        
        return {
            "avg_temperature": sum(temperatures) / len(temperatures),
            "max_temperature": max(temperatures),
            "min_temperature": min([item.temperature_min for item in forecast]),
            "dominant_condition": max(set(conditions), key=conditions.count).value,
            "avg_precipitation_chance": sum(precipitation) / len(precipitation),
            "rainy_days": len([p for p in precipitation if p > 50])
        }
        
    def _assess_content_potential(self, weather_response: WeatherResponse) -> Dict[str, Any]:
        """Assess content creation potential based on weather"""
        if not weather_response.current_weather:
            return {"potential": "unknown"}
            
        weather = weather_response.current_weather
        
        # Content potential scoring
        outdoor_score = 0.8 if weather.condition == WeatherCondition.CLEAR else 0.2
        indoor_score = 0.8 if weather.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW] else 0.4
        dramatic_score = 0.9 if weather.condition == WeatherCondition.THUNDERSTORM else 0.3
        
        return {
            "outdoor_content_potential": outdoor_score,
            "indoor_content_potential": indoor_score,
            "dramatic_content_potential": dramatic_score,
            "overall_potential": (outdoor_score + indoor_score + dramatic_score) / 3,
            "recommended_content_types": self._get_recommended_content_types(weather)
        }
        
    def _get_recommended_content_types(self, weather: WeatherData) -> List[str]:
        """Get recommended content types based on weather"""
        recommendations = []
        
        if weather.condition == WeatherCondition.CLEAR:
            recommendations.extend(["outdoor photography", "travel vlogs", "sports content"])
        elif weather.condition == WeatherCondition.RAIN:
            recommendations.extend(["indoor tutorials", "cozy lifestyle", "reading content"])
        elif weather.condition == WeatherCondition.SNOW:
            recommendations.extend(["winter activities", "holiday content", "cozy indoor scenes"])
        elif weather.condition == WeatherCondition.THUNDERSTORM:
            recommendations.extend(["dramatic photography", "storm timelapse", "indoor entertainment"])
            
        return recommendations
        
    def _compare_locations_weather(self, location_weather: Dict[str, WeatherResponse]) -> Dict[str, Any]:
        """Compare weather across locations"""
        comparison = {
            "temperature_rankings": {},
            "condition_variety": {},
            "content_opportunities": {}
        }
        
        # Temperature rankings
        temp_data = {}
        for location, weather_response in location_weather.items():
            if weather_response.current_weather:
                temp_data[location] = weather_response.current_weather.temperature
                
        sorted_temps = sorted(temp_data.items(), key=lambda x: x[1], reverse=True)
        comparison["temperature_rankings"] = {
            "warmest": sorted_temps[0] if sorted_temps else None,
            "coldest": sorted_temps[-1] if sorted_temps else None,
            "all_locations": sorted_temps
        }
        
        return comparison
        
    def _generate_multi_location_recommendations(self, location_weather: Dict[str, WeatherResponse]) -> List[str]:
        """Generate content recommendations for multiple locations"""
        recommendations = []
        
        if len(location_weather) > 1:
            recommendations.append("Create location comparison content showcasing weather differences")
            recommendations.append("Develop region-specific content tailored to local weather patterns")
            
        # Check for extreme weather
        for location, weather_response in location_weather.items():
            if weather_response.alerts:
                recommendations.append(f"Create weather safety content for {location} due to active alerts")
                
        recommendations.append("Use weather data to optimize posting schedules for each region")
        recommendations.append("Adapt content themes to match seasonal and weather patterns")
        
        return recommendations

# Factory function for easy integration
def create_weather_manager(config: Dict[str, Any]) -> WeatherServicesManager:
    """Create configured weather manager"""
    return WeatherServicesManager(config)

# Example usage for Ainflue platform
async def ainflue_weather_content_optimization_workflow(user_location: str, content_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Complete weather-based content optimization workflow for Ainflue creators
    Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
    """
    
    # Example configuration
    config = {
        "openweathermap": {
            "api_key": "your_openweathermap_api_key"
        },
        "weatherapi": {
            "api_key": "your_weatherapi_key"
        }
    }
    
    # Initialize weather manager
    weather_manager = create_weather_manager(config)
    
    # Get current weather and forecast
    weather_request = WeatherRequest(
        location=user_location,
        forecast_type=ForecastType.DAILY,
        days=7,
        include_alerts=True,
        include_air_quality=True
    )
    
    weather_response = await weather_manager.get_weather(weather_request)
    
    # Get weather-based content optimization
    content_optimizations = {}
    for plan in content_plans:
        content_type = plan.get("type", "general")
        optimization = await weather_manager.get_weather_content_optimization(
            user_location, content_type
        )
        content_optimizations[content_type] = optimization
        
    # Get location insights
    location_insights = await weather_manager.get_location_weather_insights([user_location], days=7)
    
    return {
        "location": user_location,
        "current_weather": weather_response.dict() if hasattr(weather_response, 'dict') else asdict(weather_response),
        "content_optimizations": content_optimizations,
        "location_insights": location_insights,
        "content_calendar_recommendations": {
            "optimal_posting_days": _identify_optimal_posting_days(weather_response.forecast if weather_response.success else []),
            "content_themes_by_day": _suggest_daily_themes(weather_response.forecast if weather_response.success else []),
            "engagement_predictions": _predict_weekly_engagement(weather_response.forecast if weather_response.success else [])
        },
        "monetization_insights": {
            "weather_triggered_campaigns": _suggest_weather_campaigns(weather_response.current_weather if weather_response.success else None),
            "seasonal_product_opportunities": _identify_seasonal_opportunities(weather_response.current_weather if weather_response.success else None),
            "regional_pricing_adjustments": "Consider weather-based pricing for seasonal content"
        }
    }

def _identify_optimal_posting_days(forecast: List[ForecastItem]) -> List[str]:
    """Identify optimal posting days based on weather forecast"""
    optimal_days = []
    
    for item in forecast:
        if item.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW, WeatherCondition.THUNDERSTORM]:
            optimal_days.append(f"{item.date.strftime('%A')} - High indoor engagement expected")
        elif item.condition == WeatherCondition.CLEAR and item.temperature_max < 30:
            optimal_days.append(f"{item.date.strftime('%A')} - Good outdoor content opportunity")
            
    return optimal_days

def _suggest_daily_themes(forecast: List[ForecastItem]) -> Dict[str, str]:
    """Suggest content themes for each day based on weather"""
    daily_themes = {}
    
    for item in forecast:
        day = item.date.strftime('%A')
        
        if item.condition == WeatherCondition.RAIN:
            daily_themes[day] = "Cozy indoor activities and comfort content"
        elif item.condition == WeatherCondition.CLEAR:
            daily_themes[day] = "Outdoor adventures and bright lifestyle content"
        elif item.condition == WeatherCondition.SNOW:
            daily_themes[day] = "Winter wonderland and seasonal celebration content"
        else:
            daily_themes[day] = "General lifestyle content with weather mentions"
            
    return daily_themes

def _predict_weekly_engagement(forecast: List[ForecastItem]) -> Dict[str, float]:
    """Predict engagement levels for the week based on weather"""
    engagement_predictions = {}
    
    for item in forecast:
        day = item.date.strftime('%A')
        
        # Base engagement multiplier based on weather
        if item.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW]:
            multiplier = 1.3  # Higher indoor engagement
        elif item.condition == WeatherCondition.CLEAR:
            multiplier = 0.8  # Lower engagement due to outdoor activities
        else:
            multiplier = 1.0  # Normal engagement
            
        engagement_predictions[day] = multiplier
        
    return engagement_predictions

def _suggest_weather_campaigns(current_weather: Optional[WeatherData]) -> List[str]:
    """Suggest weather-triggered marketing campaigns"""
    if not current_weather:
        return ["No weather data available for campaign suggestions"]
        
    campaigns = []
    
    if current_weather.condition == WeatherCondition.RAIN:
        campaigns.append("Rainy Day Comfort Campaign - Promote cozy content and indoor activities")
    elif current_weather.condition == WeatherCondition.CLEAR and current_weather.temperature > 25:
        campaigns.append("Summer Vibes Campaign - Promote outdoor and travel content")
    elif current_weather.temperature < 5:
        campaigns.append("Winter Warmth Campaign - Promote warm, comforting content")
        
    return campaigns

def _identify_seasonal_opportunities(current_weather: Optional[WeatherData]) -> List[str]:
    """Identify seasonal product and content opportunities"""
    if not current_weather:
        return ["No weather data available for seasonal analysis"]
        
    opportunities = []
    current_month = datetime.now().month
    
    # Seasonal opportunities based on weather and time of year
    if current_month in [12, 1, 2] and current_weather.temperature < 10:
        opportunities.append("Winter gear and cozy lifestyle product promotions")
    elif current_month in [6, 7, 8] and current_weather.temperature > 25:
        opportunities.append("Summer travel and outdoor activity content monetization")
    elif current_weather.condition == WeatherCondition.RAIN:
        opportunities.append("Indoor entertainment and comfort product partnerships")
        
    return opportunities

if __name__ == "__main__":
    # Test the weather services integration
    import asyncio
    
    async def test_weather_services():
        """Test weather services functionality"""
        
        test_location = "London, UK"
        test_content_plans = [
            {"type": "video", "theme": "lifestyle"},
            {"type": "photo", "theme": "travel"},
            {"type": "text", "theme": "motivation"}
        ]
        
        result = await ainflue_weather_content_optimization_workflow(test_location, test_content_plans)
        
        print("Weather Content Optimization Workflow Result:")
        print(json.dumps(result, indent=2, default=str))
        
    # Run test
    # asyncio.run(test_weather_services())
    
    print("✅ Weather Services Integration Module loaded successfully")
    print("🌤️ Enterprise-grade weather intelligence for Ainflue creators")
    print("📅 Weather-based content optimization, forecasting, and engagement prediction ready")