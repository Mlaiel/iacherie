"""Geolocation services"""
from typing import Optional, Tuple
import math


class GeoService:
    """Service for geolocation operations"""
    
    @staticmethod
    def calculate_distance_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1: Latitude of point 1
            lon1: Longitude of point 1
            lat2: Latitude of point 2
            lon2: Longitude of point 2
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    @staticmethod
    def geocode_address(address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        
        In production, use:
        - Google Maps Geocoding API
        - Mapbox Geocoding API
        - OpenStreetMap Nominatim
        
        Args:
            address: Address string
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        # TODO: Implement with real geocoding service
        # For now, return None
        return None
    
    @staticmethod
    def reverse_geocode(latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Address string or None
        """
        # TODO: Implement with real reverse geocoding service
        # For now, return None
        return None
    
    @staticmethod
    def get_city_from_coords(latitude: float, longitude: float) -> Optional[str]:
        """
        Get city name from coordinates
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            City name or None
        """
        # TODO: Implement with geocoding service
        return None
    
    @staticmethod
    def is_within_radius(
        center_lat: float,
        center_lon: float,
        point_lat: float,
        point_lon: float,
        radius_km: float
    ) -> bool:
        """
        Check if a point is within radius of center
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            point_lat: Point latitude
            point_lon: Point longitude
            radius_km: Radius in kilometers
            
        Returns:
            True if within radius
        """
        distance = GeoService.calculate_distance_km(
            center_lat, center_lon,
            point_lat, point_lon
        )
        return distance <= radius_km
    
    @staticmethod
    def get_bounding_box(
        latitude: float,
        longitude: float,
        radius_km: float
    ) -> Tuple[float, float, float, float]:
        """
        Get bounding box for a circle
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            
        Returns:
            Tuple of (min_lat, min_lon, max_lat, max_lon)
        """
        # Approximate degrees per km
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        min_lat = latitude - lat_delta
        max_lat = latitude + lat_delta
        min_lon = longitude - lon_delta
        max_lon = longitude + lon_delta
        
        return (min_lat, min_lon, max_lat, max_lon)
    
    @staticmethod
    def format_location_point(latitude: float, longitude: float) -> str:
        """
        Format location as PostGIS POINT
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            PostGIS POINT string
        """
        return f"POINT({longitude} {latitude})"
    
    @staticmethod
    def parse_location_point(point_str: str) -> Optional[Tuple[float, float]]:
        """
        Parse PostGIS POINT string to coordinates
        
        Args:
            point_str: PostGIS POINT string
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Extract numbers from POINT(lon lat) format
            coords = point_str.replace('POINT(', '').replace(')', '').split()
            longitude = float(coords[0])
            latitude = float(coords[1])
            return (latitude, longitude)
        except:
            return None
