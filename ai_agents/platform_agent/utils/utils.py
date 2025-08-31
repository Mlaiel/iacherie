"""Platform Agent Utils - Enterprise Utility Functions

Comprehensive utility functions for Platform Agent components with
advanced features for content processing, security, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import os
import re
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import aiofiles
import json
import base64
from urllib.parse import urlparse, parse_qs
import time
import random
from functools import wraps, lru_cache
from contextlib import asynccontextmanager
import tempfile
import shutil

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

from .exceptions import (
    FileOperationException,
    SecurityException,
    ContentFormatException,
    ValidationException
)


# Content Type Detection
CONTENT_TYPE_MAP = {
    # Audio formats
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.flac': 'audio/flac',
    '.aac': 'audio/aac',
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/mp4',
    '.wma': 'audio/x-ms-wma',
    
    # Video formats
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.mkv': 'video/x-matroska',
    '.webm': 'video/webm',
    '.flv': 'video/x-flv',
    '.wmv': 'video/x-ms-wmv',
    '.3gp': 'video/3gpp',
    
    # Image formats
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.tiff': 'image/tiff',
    '.svg': 'image/svg+xml',
    
    # Document formats
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.csv': 'text/csv'
}

# Social Media Platform Limits
PLATFORM_LIMITS = {
    'spotify': {
        'max_audio_size': 100 * 1024 * 1024,  # 100MB
        'max_duration': 600,  # 10 minutes
        'supported_formats': ['mp3', 'wav', 'flac'],
        'max_description_length': 1000,
        'max_title_length': 100
    },
    'youtube': {
        'max_video_size': 128 * 1024 * 1024 * 1024,  # 128GB
        'max_duration': 12 * 3600,  # 12 hours
        'supported_formats': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        'max_description_length': 5000,
        'max_title_length': 100,
        'max_tags': 500
    },
    'instagram': {
        'max_image_size': 8 * 1024 * 1024,  # 8MB
        'max_video_size': 100 * 1024 * 1024,  # 100MB
        'max_video_duration': 60,  # 60 seconds for posts
        'max_story_duration': 15,  # 15 seconds for stories
        'supported_image_formats': ['jpg', 'png'],
        'supported_video_formats': ['mp4', 'mov'],
        'max_caption_length': 2200,
        'max_hashtags': 30,
        'aspect_ratios': [(1, 1), (4, 5), (16, 9)]
    },
    'tiktok': {
        'max_video_size': 287 * 1024 * 1024,  # 287MB
        'max_duration': 180,  # 3 minutes
        'min_duration': 3,  # 3 seconds
        'supported_formats': ['mp4', 'mov', 'avi'],
        'max_description_length': 300,
        'recommended_resolution': (1080, 1920),
        'aspect_ratio': (9, 16)
    },
    'twitter': {
        'max_image_size': 5 * 1024 * 1024,  # 5MB
        'max_video_size': 512 * 1024 * 1024,  # 512MB
        'max_video_duration': 140,  # 2:20 minutes
        'supported_image_formats': ['jpg', 'png', 'gif', 'webp'],
        'supported_video_formats': ['mp4', 'mov'],
        'max_text_length': 280,
        'max_images_per_tweet': 4
    },
    'facebook': {
        'max_image_size': 10 * 1024 * 1024,  # 10MB
        'max_video_size': 4 * 1024 * 1024 * 1024,  # 4GB
        'max_video_duration': 240 * 60,  # 240 minutes
        'supported_image_formats': ['jpg', 'png', 'gif', 'bmp', 'tiff'],
        'supported_video_formats': ['mp4', 'mov', 'avi', 'mkv'],
        'max_post_length': 63206,
        'recommended_image_size': (1200, 630)
    },
    'linkedin': {
        'max_image_size': 10 * 1024 * 1024,  # 10MB
        'max_video_size': 200 * 1024 * 1024,  # 200MB
        'max_video_duration': 600,  # 10 minutes
        'supported_image_formats': ['jpg', 'png', 'gif'],
        'supported_video_formats': ['mp4', 'mov', 'wmv', 'flv'],
        'max_post_length': 1300,
        'max_headline_length': 150
    }
}


class SecurityUtils:
    """Security utilities for encryption, hashing, and token management"""    
    @staticmethod
    def generate_key_from_password(password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """Encrypt data using Fernet encryption"""        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """Decrypt data using Fernet encryption"""        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt using SHA-256"""        if salt is None:
            salt = os.urandom(32).hex()
        
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode(), 
                                          salt.encode(), 
                                          100000)
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""        computed_hash, _ = SecurityUtils.hash_password(password, salt)
        return computed_hash == password_hash
    
    @staticmethod
    def generate_jwt_token(payload: Dict[str, Any], secret_key: str, 
                          expires_in: int = 3600) -> str:
        """Generate JWT token"""        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise SecurityException("Token has expired")
        except jwt.InvalidTokenError:
            raise SecurityException("Invalid token")
    
    @staticmethod
    def generate_secure_filename(filename: str) -> str:
        """Generate secure filename"""        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove special characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        # Add timestamp to avoid conflicts
        timestamp = int(time.time())
        return f"{name}_{timestamp}{ext}"
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """Sanitize user input"""        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        # Remove potentially dangerous characters
        input_str = re.sub(r'[<>"\']', '', input_str)
        
        # Limit length
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        return input_str.strip()


class FileUtils:
    """File handling utilities"""    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Get file type from extension"""        ext = Path(file_path).suffix.lower()
        return CONTENT_TYPE_MAP.get(ext, 'application/octet-stream')
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""        return os.path.getsize(file_path)
    
    @staticmethod
    def is_supported_format(file_path: str, platform: str) -> bool:
        """Check if file format is supported by platform"""        ext = Path(file_path).suffix.lower()[1:]  # Remove dot
        platform_config = PLATFORM_LIMITS.get(platform.lower(), {})
        
        supported_formats = []
        if 'supported_formats' in platform_config:
            supported_formats.extend(platform_config['supported_formats'])
        if 'supported_image_formats' in platform_config:
            supported_formats.extend(platform_config['supported_image_formats'])
        if 'supported_video_formats' in platform_config:
            supported_formats.extend(platform_config['supported_video_formats'])
        
        return ext in supported_formats
    
    @staticmethod
    async def validate_file_size(file_path: str, platform: str) -> bool:
        """Validate file size against platform limits"""        file_size = FileUtils.get_file_size(file_path)
        platform_config = PLATFORM_LIMITS.get(platform.lower(), {})
        
        # Check different size limits based on file type
        file_type = FileUtils.get_file_type(file_path)
        
        if file_type.startswith('image/'):
            max_size = platform_config.get('max_image_size', float('inf'))
        elif file_type.startswith('video/'):
            max_size = platform_config.get('max_video_size', float('inf'))
        elif file_type.startswith('audio/'):
            max_size = platform_config.get('max_audio_size', float('inf'))
        else:
            max_size = platform_config.get('max_file_size', float('inf'))
        
        return file_size <= max_size
    
    @staticmethod
    def generate_file_hash(file_path: str) -> str:
        """Generate SHA-256 hash of file"""        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    async def create_temp_file(content: bytes, suffix: str = None) -> str:
        """Create temporary file with content"""        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            temp_file.write(content)
            temp_file.flush()
            return temp_file.name
        finally:
            temp_file.close()
    
    @staticmethod
    async def read_file_chunks(file_path: str, chunk_size: int = 8192):
        """Read file in chunks (async generator)"""        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    @staticmethod
    def cleanup_temp_files(file_paths: List[str]):
        """Clean up temporary files"""        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass  # Ignore cleanup errors


class TextUtils:
    """Text processing utilities"""    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length"""        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text"""        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        return [mention[1:] for mention in mentions]  # Remove @ symbol
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for platform posting"""        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove or replace problematic characters
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    @staticmethod
    def generate_seo_title(title: str, keywords: List[str], max_length: int = 60) -> str:
        """Generate SEO-optimized title"""        if not keywords:
            return TextUtils.truncate_text(title, max_length)
        
        # Try to include keywords naturally
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            if keyword.lower() not in title.lower() and len(title) + len(keyword) + 3 <= max_length:
                title = f"{title} | {keyword}"
        
        return TextUtils.truncate_text(title, max_length)
    
    @staticmethod
    def generate_description_with_hashtags(description: str, hashtags: List[str], 
                                         max_length: int = 1000) -> str:
        """Generate description with hashtags"""        hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
        
        available_length = max_length - len(hashtag_text) - 2  # Space for hashtags and separator
        
        if len(description) > available_length:
            description = TextUtils.truncate_text(description, available_length)
        
        return f"{description}\n\n{hashtag_text}" if hashtags else description
    
    @staticmethod
    def validate_platform_text(text: str, platform: str, text_type: str = 'post') -> bool:
        """Validate text against platform limits"""        platform_config = PLATFORM_LIMITS.get(platform.lower(), {})
        
        if text_type == 'title':
            max_length = platform_config.get('max_title_length', float('inf'))
        elif text_type == 'description':
            max_length = platform_config.get('max_description_length', float('inf'))
        elif text_type == 'caption':
            max_length = platform_config.get('max_caption_length', float('inf'))
        else:
            max_length = platform_config.get('max_post_length', float('inf'))
        
        return len(text) <= max_length


class URLUtils:
    """URL handling utilities"""    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL"""        try:
            return urlparse(url).netloc
        except Exception:
            return None
    
    @staticmethod
    def build_callback_url(base_url: str, params: Dict[str, str]) -> str:
        """Build callback URL with parameters"""        if not params:
            return base_url
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}{param_string}"
    
    @staticmethod
    def parse_query_params(url: str) -> Dict[str, List[str]]:
        """Parse query parameters from URL"""        parsed = urlparse(url)
        return parse_qs(parsed.query)


class AsyncUtils:
    """Asynchronous programming utilities"""    
    @staticmethod
    def retry_async(max_attempts: int = 3, delay: float = 1.0, 
                   exponential_backoff: bool = True):
        """Decorator for async function retry with exponential backoff"""        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            wait_time = delay * (2 ** attempt) if exponential_backoff else delay
                            await asyncio.sleep(wait_time)
                        else:
                            raise last_exception
                
                return None
            return wrapper
        return decorator
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float):
        """Run coroutine with timeout"""        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    async def gather_with_concurrency(tasks: List, max_concurrency: int = 10):
        """Run tasks with limited concurrency"""        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def run_task(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(*[run_task(task) for task in tasks])
    
    @staticmethod
    @asynccontextmanager
    async def async_lock_with_timeout(lock: asyncio.Lock, timeout: float = 30.0):
        """Acquire lock with timeout"""        try:
            await asyncio.wait_for(lock.acquire(), timeout=timeout)
            yield
        except asyncio.TimeoutError:
            raise TimeoutError(f"Failed to acquire lock within {timeout} seconds")
        finally:
            if lock.locked():
                lock.release()


class RateLimiter:
    """Rate limiting utility"""    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""        now = time.time()
        window_start = now - self.time_window
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_retry_after(self, identifier: str) -> int:
        """Get seconds to wait before retry"""        if identifier not in self.requests or not self.requests[identifier]:
            return 0
        
        oldest_request = min(self.requests[identifier])
        retry_after = self.time_window - (time.time() - oldest_request)
        return max(0, int(retry_after))


class CacheUtils:
    """Caching utilities"""    
    @staticmethod
    @lru_cache(maxsize=128)
    def cached_platform_limits(platform: str) -> Dict[str, Any]:
        """Get cached platform limits"""        return PLATFORM_LIMITS.get(platform.lower(), {})
    
    @staticmethod
    def generate_cache_key(*args) -> str:
        """Generate cache key from arguments"""        key_parts = []
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()


class ValidationUtils:
    """Data validation utilities"""    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""        pattern = r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_content_metadata(metadata: Dict[str, Any]) -> List[str]:
        """Validate content metadata and return errors"""        errors = []
        
        required_fields = ['title', 'description', 'content_type']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'tags' in metadata and isinstance(metadata['tags'], list):
            if len(metadata['tags']) > 50:
                errors.append("Too many tags (maximum 50)")
        
        if 'duration' in metadata and metadata['duration'] < 0:
            errors.append("Duration cannot be negative")
        
        return errors


class DateTimeUtils:
    """Date and time utilities"""    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime"""        return datetime.now(timezone.utc)
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S UTC') -> str:
        """Format datetime to string"""        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> datetime:
        """Parse datetime from string"""        return datetime.strptime(date_str, format_str).replace(tzinfo=timezone.utc)
    
    @staticmethod
    def is_business_hours(dt: datetime, timezone_offset: int = 0) -> bool:
        """Check if datetime is in business hours (9 AM - 5 PM)"""        local_dt = dt + timedelta(hours=timezone_offset)
        return 9 <= local_dt.hour < 17 and local_dt.weekday() < 5
    
    @staticmethod
    def get_optimal_posting_time(timezone_offset: int = 0) -> datetime:
        """Get optimal posting time based on engagement data"""        now = DateTimeUtils.utc_now()
        local_now = now + timedelta(hours=timezone_offset)
        
        # Peak engagement times: 9 AM, 1 PM, 5 PM
        peak_hours = [9, 13, 17]
        
        for hour in peak_hours:
            if local_now.hour < hour:
                optimal_time = local_now.replace(hour=hour, minute=0, second=0, microsecond=0)
                return optimal_time - timedelta(hours=timezone_offset)
        
        # If past all peak hours, schedule for next day 9 AM
        next_day = local_now + timedelta(days=1)
        optimal_time = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        return optimal_time - timedelta(hours=timezone_offset)


class MetricsUtils:
    """Metrics and analytics utilities"""    
    @staticmethod
    def calculate_engagement_rate(likes: int, comments: int, shares: int, 
                                views: int) -> float:
        """Calculate engagement rate"""        if views == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100
    
    @staticmethod
    def calculate_virality_score(shares: int, views: int, time_hours: float) -> float:
        """Calculate virality score"""        if views == 0 or time_hours == 0:
            return 0.0
        
        share_rate = shares / views
        velocity = shares / time_hours
        
        return (share_rate * 100) + (velocity * 10)
    
    @staticmethod
    def calculate_quality_score(metrics: Dict[str, Any]) -> float:
        """Calculate content quality score based on metrics"""        weights = {
            'engagement_rate': 0.4,
            'completion_rate': 0.3,
            'share_rate': 0.2,
            'save_rate': 0.1
        }
        
        score = 0.0
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
        
        return min(100.0, max(0.0, score))


# Global utility instances
security_utils = SecurityUtils()
file_utils = FileUtils()
text_utils = TextUtils()
url_utils = URLUtils()
async_utils = AsyncUtils()
validation_utils = ValidationUtils()
datetime_utils = DateTimeUtils()
metrics_utils = MetricsUtils()
cache_utils = CacheUtils()

# Rate limiter instances for different operations
upload_rate_limiter = RateLimiter(max_requests=10, time_window=60)  # 10 uploads per minute
api_rate_limiter = RateLimiter(max_requests=100, time_window=3600)  # 100 API calls per hour
