"""
 COLLABORATION UTILS - Utility Functions & Helpers
==================================================

Developed by: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved - Unauthorized use is strictly prohibited

  LEGAL WARNING 
This code is the exclusive property of Fahed Mlaiel.
Any attempt to steal, copy, or reproduce this concept, idea, or code
without explicit written authorization from Fahed Mlaiel is strictly forbidden
and will result in immediate legal action under German and international law.

Comprehensive utility functions for collaboration system operations.
Advanced helpers for data processing, validation, and system operations.

Features:
- Advanced Data Validation & Sanitization
- Comprehensive Date/Time Utilities with Timezone Support
- Robust Encryption & Security Utilities
- Advanced Text Processing & NLP Helpers
- File Upload & Media Processing Utilities
- Geographic & Location Processing Tools
- Performance Monitoring & Profiling Utilities
- Database Query Optimization Helpers
- Cache Management & Optimization Tools
- Error Handling & Logging Utilities
- API Response Formatting & Pagination
- Data Serialization & Transformation
- Image & Video Processing Helpers
- Audio Analysis & Processing Tools
- ML Model Utility Functions
- Webhook Processing & Validation
- Rate Limiting & Throttling Utilities
- Notification Formatting Helpers
"""

import asyncio
import logging
import functools
import time
import hashlib
import uuid
import re
import mimetypes
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, TypeVar, Generic
from dataclasses import dataclass, asdict
from enum import Enum
import json
import yaml
import csv
import io
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlparse, parse_qs
import requests
from PIL import Image, ImageOps, ImageEnhance
import cv2
import librosa
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pytz
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import jwt
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import PhoneNumberFormat
import bleach
from markupsafe import Markup
import magic
from sqlalchemy import text
import redis
from elasticsearch import Elasticsearch
import boto3
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ValidationError(Exception):
    """Custom validation error"""
    pass

class ProcessingError(Exception):
    """Custom processing error"""
    pass

# ==============================================================================
# PERFORMANCE & MONITORING UTILITIES
# ==============================================================================

def async_timer(func: Callable) -> Callable:
    """Decorator to measure async function execution time"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying failed operations with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
                        
            raise last_exception
        return wrapper
    return decorator

# ==============================================================================
# VALIDATION UTILITIES
# ==============================================================================

class DataValidator:
    """Comprehensive data validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""



        try:
            validation = validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone(phone: str, region: str = "US") -> bool:
        """Validate phone number"""



        try:
            parsed = phonenumbers.parse(phone, region)
            return phonenumbers.is_valid_number(parsed)
        except phonenumbers.NumberParseException:
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""



        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""



        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_json(json_string: str) -> bool:
        """Validate JSON format"""



        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """Sanitize HTML content"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        allowed_attributes = {'a': ['href', 'title'], '*': ['class']}
        return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            'is_valid': True,
            'score': 0,
            'issues': []
        }
        
        if len(password) < 8:
            result['issues'].append('Password must be at least 8 characters long')
            result['is_valid'] = False
        else:
            result['score'] += 1
            
        if not re.search(r'[A-Z]', password):
            result['issues'].append('Password must contain at least one uppercase letter')
            result['is_valid'] = False
        else:
            result['score'] += 1
            
        if not re.search(r'[a-z]', password):
            result['issues'].append('Password must contain at least one lowercase letter')
            result['is_valid'] = False
        else:
            result['score'] += 1
            
        if not re.search(r'\d', password):
            result['issues'].append('Password must contain at least one digit')
            result['is_valid'] = False
        else:
            result['score'] += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['issues'].append('Password must contain at least one special character')
        else:
            result['score'] += 1
            
        # Calculate strength
        if result['score'] >= 4:
            result['strength'] = 'Strong'
        elif result['score'] >= 3:
            result['strength'] = 'Medium'
        else:
            result['strength'] = 'Weak'
            
        return result

# ==============================================================================
# DATETIME UTILITIES
# ==============================================================================

class DateTimeUtils:
    """Advanced datetime utilities with timezone support"""
    
    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC datetime"""



        return datetime.now(timezone.utc)
    
    @staticmethod
    def to_timezone(dt: datetime, timezone_name: str) -> datetime:
        """Convert datetime to specific timezone"""
        tz = pytz.timezone(timezone_name)
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(tz)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    @staticmethod
    def parse_iso_datetime(iso_string: str) -> datetime:
        """Parse ISO format datetime string"""



        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def get_business_hours(timezone_name: str = "UTC") -> Dict[str, Any]:
        """Get business hours for timezone"""
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        
        return {
            'current_time': now.isoformat(),
            'is_business_hours': 9 <= now.hour <= 17 and now.weekday() < 5,
            'next_business_day': DateTimeUtils._next_business_day(now),
            'timezone': timezone_name
        }
    
    @staticmethod
    def _next_business_day(dt: datetime) -> datetime:
        """Calculate next business day"""
        next_day = dt + timedelta(days=1)
        while next_day.weekday() >= 5:  # Skip weekends
            next_day += timedelta(days=1)
        return next_day.replace(hour=9, minute=0, second=0, microsecond=0)

# ==============================================================================
# ENCRYPTION & SECURITY UTILITIES
# ==============================================================================

class SecurityUtils:
    """Advanced security and encryption utilities"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key:
            self.fernet = Fernet(key)
        else:
            self.fernet = Fernet(Fernet.generate_key())
    
    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt string and return base64 encoded result"""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded encrypted string"""
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""



        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""



        return base64.urlsafe_b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)[:length].decode()
    
    @staticmethod
    def generate_jwt(payload: Dict[str, Any], secret: str, expiry_hours: int = 24) -> str:
        """Generate JWT token"""
        payload['exp'] = datetime.utcnow() + timedelta(hours=expiry_hours)
        payload['iat'] = datetime.utcnow()
        return jwt.encode(payload, secret, algorithm='HS256')
    
    @staticmethod
    def verify_jwt(token: str, secret: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""



        try:
            return jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None

# ==============================================================================
# TEXT PROCESSING UTILITIES
# ==============================================================================

class TextUtils:
    """Advanced text processing and NLP utilities"""
    
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
        
        # Strip leading/trailing whitespace
        return text.strip()
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""



        return re.findall(r'#(\w+)', text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text"""



        return re.findall(r'@(\w+)', text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def truncate_text(text: str, max_length: int, ellipsis: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(ellipsis)] + ellipsis
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug"""
        # Convert to lowercase
        text = text.lower()
        
        # Replace spaces and special characters with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        
        # Strip leading/trailing hyphens
        return text.strip('-')
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment"""



        try:
            result = self.sentiment_analyzer(text)[0]
            return {
                'label': result['label'],
                'score': result['score'],
                'confidence': 'high' if result['score'] > 0.8 else 'medium' if result['score'] > 0.6 else 'low'
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'label': 'UNKNOWN', 'score': 0.0, 'confidence': 'low'}

# ==============================================================================
# MEDIA PROCESSING UTILITIES
# ==============================================================================

class MediaUtils:
    """Advanced media processing utilities"""
    
    @staticmethod
    def process_image(
        image_path: str,
        output_path: str,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85
    ) -> Dict[str, Any]:
        """Process and optimize image"""



        try:
            with Image.open(image_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                
                # Calculate new dimensions maintaining aspect ratio
                ratio = min(max_width / original_width, max_height / original_height)
                if ratio < 1:
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Save optimized image
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                return {
                    'success': True,
                    'original_size': (original_width, original_height),
                    'new_size': img.size,
                    'compression_ratio': MediaUtils._get_file_size(image_path) / MediaUtils._get_file_size(output_path)
                }
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def extract_video_thumbnail(video_path: str, output_path: str, timestamp: float = 1.0) -> bool:
        """Extract thumbnail from video"""



        try:
            cap = cv2.VideoCapture(video_path)
            
            # Set timestamp
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(output_path, frame)
                cap.release()
                return True
            else:
                cap.release()
                return False
                
        except Exception as e:
            logger.error(f"Error extracting video thumbnail: {str(e)}")
            return False
    
    @staticmethod
    def analyze_audio(audio_path: str) -> Dict[str, Any]:
        """Analyze audio file"""



        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Calculate features
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
            
            return {
                'duration': float(duration),
                'tempo': float(tempo),
                'avg_spectral_centroid': float(np.mean(spectral_centroids)),
                'avg_zero_crossing_rate': float(np.mean(zero_crossings)),
                'sample_rate': sr,
                'channels': 1,  # librosa loads as mono by default
                'file_size': MediaUtils._get_file_size(audio_path)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def _get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        import os
        return os.path.getsize(file_path)

# ==============================================================================
# GEOGRAPHIC UTILITIES
# ==============================================================================

class GeoUtils:
    """Geographic and location utilities"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="collaboration_system")
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate distance between two geographic points in kilometers"""



        return geodesic(point1, point2).kilometers
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode address to coordinates"""



        try:
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                    'raw': location.raw
                }
            return None
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode coordinates to address"""



        try:
            location = self.geolocator.reverse((latitude, longitude), timeout=10)
            if location:
                return {
                    'address': location.address,
                    'raw': location.raw
                }
            return None
        except Exception as e:
            logger.error(f"Error reverse geocoding: {str(e)}")
            return None
    
    @staticmethod
    def get_timezone_from_coordinates(latitude: float, longitude: float) -> str:
        """Get timezone from coordinates (simplified)"""
        # This is a simplified implementation
        # In production, use a proper timezone API
        if -180 <= longitude < -150:
            return "Pacific/Honolulu"
        elif -150 <= longitude < -120:
            return "America/Anchorage"
        elif -120 <= longitude < -90:
            return "America/Los_Angeles"
        elif -90 <= longitude < -75:
            return "America/Chicago"
        elif -75 <= longitude < -60:
            return "America/New_York"
        else:
            return "UTC"

# ==============================================================================
# DATA FORMATTING UTILITIES
# ==============================================================================

class FormatUtils:
    """Data formatting and serialization utilities"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "USD", locale: str = "en_US") -> str:
        """Format currency amount"""
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    
    @staticmethod
    def format_number(number: Union[int, float], precision: int = 2) -> str:
        """Format number with thousand separators"""
        if isinstance(number, int):
            return f"{number:,}"
        else:
            return f"{number:,.{precision}f}"
    
    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """Format percentage"""



        return f"{value * 100:.{precision}f}%"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.1f} GB"
    
    @staticmethod
    def serialize_datetime(dt: datetime) -> str:
        """Serialize datetime to ISO format"""



        return dt.isoformat()
    
    @staticmethod
    def deserialize_datetime(iso_string: str) -> datetime:
        """Deserialize ISO format datetime"""



        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """Convert camelCase to snake_case"""



        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()

# ==============================================================================
# PAGINATION UTILITIES
# ==============================================================================

@dataclass
class PaginationInfo:
    """Pagination information"""
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_prev: bool
    has_next: bool
    prev_page: Optional[int]
    next_page: Optional[int]

class PaginationUtils:
    """Pagination utilities"""
    
    @staticmethod
    def paginate(
        items: List[T],
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ) -> Tuple[List[T], PaginationInfo]:
        """Paginate list of items"""
        # Validate inputs
        page = max(1, page)
        per_page = min(max(1, per_page), max_per_page)
        
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get page items
        page_items = items[offset:offset + per_page]
        
        # Create pagination info
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_prev=page > 1,
            has_next=page < total_pages,
            prev_page=page - 1 if page > 1 else None,
            next_page=page + 1 if page < total_pages else None
        )
        
        return page_items, pagination
    
    @staticmethod
    def create_pagination_response(
        data: List[Any],
        pagination: PaginationInfo,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized pagination response"""



        return {
            'data': data,
            'pagination': asdict(pagination),
            'meta': meta or {}
        }

# ==============================================================================
# CACHE UTILITIES
# ==============================================================================

class CacheUtils:
    """Advanced caching utilities"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get_or_set(
        self,
        key: str,
        factory_func: Callable[[], Any],
        ttl: int = 3600
    ) -> Any:
        """Get from cache or set using factory function"""



        try:
            # Try to get from cache
            cached_value = await self.redis.get(key)
            if cached_value:
                return json.loads(cached_value)
            
            # Generate new value
            value = await factory_func() if asyncio.iscoroutinefunction(factory_func) else factory_func()
            
            # Cache the value
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            
            return value
            
        except Exception as e:
            logger.error(f"Cache error for key {key}: {str(e)}")
            # Fallback to factory function
            return await factory_func() if asyncio.iscoroutinefunction(factory_func) else factory_func()
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""



        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {str(e)}")
            return 0

# Export main utilities
__all__ = [
    'DataValidator',
    'DateTimeUtils', 
    'SecurityUtils',
    'TextUtils',
    'MediaUtils',
    'GeoUtils',
    'FormatUtils',
    'PaginationUtils',
    'PaginationInfo',
    'CacheUtils',
    'ValidationError',
    'ProcessingError',
    'async_timer',
    'retry_on_failure'
]
