"""Cookie Manager Module
=====================

Professional cookie management for web crawling operations.
Implements intelligent cookie handling with persistence and security features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""import json
import logging
import pickle
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from http.cookies import SimpleCookie
from urllib.parse import urlparse
import aiofiles
import redis
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class CookieData:
    """Cookie data structure."""    name: str
    value: str
    domain: str
    path: str = "/"
    expires: Optional[datetime] = None
    max_age: Optional[int] = None
    secure: bool = False
    http_only: bool = False
    same_site: Optional[str] = None
    created_at: datetime = None
    last_used: datetime = None
    use_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_used is None:
            self.last_used = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if cookie is expired."""        if self.expires:
            return datetime.utcnow() > self.expires
        if self.max_age:
            expiry_time = self.created_at + timedelta(seconds=self.max_age)
            return datetime.utcnow() > expiry_time
        return False

    def is_valid_for_domain(self, domain: str) -> bool:
        """Check if cookie is valid for given domain."""        if self.domain.startswith('.'):
            # Domain cookie
            return domain.endswith(self.domain[1:])
        else:
            # Host cookie
            return domain == self.domain

    def to_dict(self) -> Dict:
        """Convert to dictionary."""        data = asdict(self)
        if data['expires']:
            data['expires'] = data['expires'].isoformat()
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['last_used']:
            data['last_used'] = data['last_used'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'CookieData':
        """Create from dictionary."""        if data.get('expires'):
            data['expires'] = datetime.fromisoformat(data['expires'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)

class CookieJar:
    """    Professional cookie jar implementation.
    
    Features:
    - Domain-based cookie storage
    - Expiration management
    - Security validation
    - Persistence support
    - Cookie sharing policies
    """    
    def __init__(self):
        """Initialize cookie jar."""        self.cookies: Dict[str, Dict[str, CookieData]] = {}
        self.policy = CookiePolicy()
    
    def add_cookie(self, cookie: CookieData) -> None:
        """Add cookie to jar."""        # Validate cookie
        if not self.policy.should_accept_cookie(cookie):
            logger.debug(f"Cookie rejected by policy: {cookie.name}")
            return
        
        domain = cookie.domain
        if domain not in self.cookies:
            self.cookies[domain] = {}
        
        # Update existing or add new
        existing = self.cookies[domain].get(cookie.name)
        if existing:
            # Update usage statistics
            cookie.use_count = existing.use_count
            cookie.created_at = existing.created_at
        
        cookie.last_used = datetime.utcnow()
        self.cookies[domain][cookie.name] = cookie
        
        logger.debug(f"Added cookie: {cookie.name} for domain {domain}")
    
    def get_cookies_for_domain(self, domain: str, path: str = "/") -> List[CookieData]:
        """Get all valid cookies for domain and path."""        valid_cookies = []
        
        # Clean expired cookies first
        self._clean_expired_cookies()
        
        # Check all domains
        for cookie_domain, domain_cookies in self.cookies.items():
            for cookie_name, cookie in domain_cookies.items():
                if cookie.is_valid_for_domain(domain) and self._path_matches(cookie.path, path):
                    if not cookie.is_expired():
                        cookie.last_used = datetime.utcnow()
                        cookie.use_count += 1
                        valid_cookies.append(cookie)
        
        return valid_cookies
    
    def _path_matches(self, cookie_path: str, request_path: str) -> bool:
        """Check if cookie path matches request path."""        if cookie_path == "/":
            return True
        return request_path.startswith(cookie_path)
    
    def get_cookie_header(self, domain: str, path: str = "/") -> str:
        """Get cookie header string for domain."""        cookies = self.get_cookies_for_domain(domain, path)
        cookie_pairs = [f"{cookie.name}={cookie.value}" for cookie in cookies]
        return "; ".join(cookie_pairs)
    
    def remove_cookie(self, domain: str, name: str) -> bool:
        """Remove specific cookie."""        if domain in self.cookies and name in self.cookies[domain]:
            del self.cookies[domain][name]
            logger.debug(f"Removed cookie: {name} from domain {domain}")
            return True
        return False
    
    def clear_domain_cookies(self, domain: str) -> None:
        """Clear all cookies for domain."""        if domain in self.cookies:
            del self.cookies[domain]
            logger.debug(f"Cleared all cookies for domain: {domain}")
    
    def clear_all_cookies(self) -> None:
        """Clear all cookies."""        self.cookies.clear()
        logger.debug("Cleared all cookies")
    
    def _clean_expired_cookies(self) -> None:
        """Remove expired cookies."""        domains_to_remove = []
        
        for domain, domain_cookies in self.cookies.items():
            cookies_to_remove = []
            
            for name, cookie in domain_cookies.items():
                if cookie.is_expired():
                    cookies_to_remove.append(name)
            
            for name in cookies_to_remove:
                del domain_cookies[name]
                logger.debug(f"Removed expired cookie: {name} from {domain}")
            
            if not domain_cookies:
                domains_to_remove.append(domain)
        
        for domain in domains_to_remove:
            del self.cookies[domain]
    
    def get_cookie_count(self) -> int:
        """Get total cookie count."""        return sum(len(domain_cookies) for domain_cookies in self.cookies.values())
    
    def get_domains(self) -> Set[str]:
        """Get all domains with cookies."""        return set(self.cookies.keys())

class CookiePolicy:
    """    Cookie acceptance and security policy.
    
    Features:
    - Security validation
    - Size limits
    - Domain restrictions
    - Content filtering
    """    
    def __init__(self):
        """Initialize cookie policy."""        self.max_cookie_size = 4096  # RFC 6265 recommendation
        self.max_cookies_per_domain = 50
        self.max_total_cookies = 3000
        self.blocked_domains: Set[str] = set()
        self.allowed_domains: Set[str] = set()
        self.require_secure = False
        self.block_third_party = False
    
    def should_accept_cookie(self, cookie: CookieData) -> bool:
        """Determine if cookie should be accepted."""        # Size check
        if len(cookie.value) > self.max_cookie_size:
            logger.debug(f"Cookie too large: {len(cookie.value)} bytes")
            return False
        
        # Domain restrictions
        if self.blocked_domains and cookie.domain in self.blocked_domains:
            logger.debug(f"Domain blocked: {cookie.domain}")
            return False
        
        if self.allowed_domains and cookie.domain not in self.allowed_domains:
            logger.debug(f"Domain not in allowlist: {cookie.domain}")
            return False
        
        # Security requirements
        if self.require_secure and not cookie.secure:
            logger.debug(f"Insecure cookie rejected: {cookie.name}")
            return False
        
        # Content validation
        if not self._is_valid_cookie_value(cookie.value):
            logger.debug(f"Invalid cookie value: {cookie.name}")
            return False
        
        return True
    
    def _is_valid_cookie_value(self, value: str) -> bool:
        """Validate cookie value content."""        # Check for suspicious patterns
        suspicious_patterns = [
            '<script',
            'javascript:',
            'data:',
            'vbscript:',
        ]
        
        value_lower = value.lower()
        for pattern in suspicious_patterns:
            if pattern in value_lower:
                return False
        
        return True

class CookieManager:
    """    Enterprise cookie manager with persistence and encryption.
    
    Features:
    - Multiple storage backends
    - Encryption for sensitive cookies
    - Automatic cleanup
    - Session management
    - Concurrent access support
    """    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        encryption_key: Optional[bytes] = None,
        redis_client: Optional[redis.Redis] = None,
        enable_encryption: bool = True
    ):
        """Initialize cookie manager."""        self.cookie_jar = CookieJar()
        self.storage_path = storage_path or Path("cookies.db")
        self.redis_client = redis_client
        self.enable_encryption = enable_encryption
        
        # Setup encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        elif enable_encryption:
            # Generate new key if none provided
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            logger.warning("Generated new encryption key. Store it securely!")
        else:
            self.cipher = None
        
        # Initialize storage
        self._init_storage()
    
    def _init_storage(self) -> None:
        """Initialize storage backend."""        if self.storage_path:
            self._init_sqlite_storage()
    
    def _init_sqlite_storage(self) -> None:
        """Initialize SQLite storage."""        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            cursor.execute("""                CREATE TABLE IF NOT EXISTS cookies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    path TEXT DEFAULT '/',
                    expires TEXT,
                    max_age INTEGER,
                    secure BOOLEAN DEFAULT FALSE,
                    http_only BOOLEAN DEFAULT FALSE,
                    same_site TEXT,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL,
                    use_count INTEGER DEFAULT 0,
                    encrypted BOOLEAN DEFAULT FALSE,
                    UNIQUE(domain, name, path)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLite storage: {e}")
    
    async def add_cookies_from_response(self, url: str, set_cookie_header: str) -> None:
        """Add cookies from HTTP Set-Cookie header."""        try:
            domain = urlparse(url).netloc
            
            # Parse Set-Cookie header
            cookie = SimpleCookie()
            cookie.load(set_cookie_header)
            
            for name, morsel in cookie.items():
                cookie_data = CookieData(
                    name=name,
                    value=morsel.value,
                    domain=morsel.get('domain', domain),
                    path=morsel.get('path', '/'),
                    secure=bool(morsel.get('secure')),
                    http_only=bool(morsel.get('httponly')),
                    same_site=morsel.get('samesite')
                )
                
                # Handle expires
                if morsel.get('expires'):
                    try:
                        cookie_data.expires = datetime.strptime(
                            morsel['expires'], 
                            '%a, %d %b %Y %H:%M:%S %Z'
                        )
                    except ValueError:
                        pass
                
                # Handle max-age
                if morsel.get('max-age'):
                    try:
                        cookie_data.max_age = int(morsel['max-age'])
                    except ValueError:
                        pass
                
                self.cookie_jar.add_cookie(cookie_data)
                
                # Persist to storage
                await self._persist_cookie(cookie_data)
                
        except Exception as e:
            logger.error(f"Failed to add cookies from response: {e}")
    
    async def get_cookie_header_for_request(self, url: str) -> str:
        """Get cookie header for outgoing request."""        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path or "/"
            
            return self.cookie_jar.get_cookie_header(domain, path)
            
        except Exception as e:
            logger.error(f"Failed to get cookie header: {e}")
            return ""
    
    async def load_cookies(self) -> None:
        """Load cookies from persistent storage."""        if self.redis_client:
            await self._load_from_redis()
        elif self.storage_path:
            await self._load_from_sqlite()
    
    async def save_cookies(self) -> None:
        """Save cookies to persistent storage."""        if self.redis_client:
            await self._save_to_redis()
        elif self.storage_path:
            await self._save_to_sqlite()
    
    async def _load_from_sqlite(self) -> None:
        """Load cookies from SQLite."""        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM cookies")
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            
            for row in rows:
                data = dict(zip(columns, row))
                
                # Decrypt if needed
                if data['encrypted'] and self.cipher:
                    try:
                        data['value'] = self.cipher.decrypt(data['value'].encode()).decode()
                    except Exception as e:
                        logger.warning(f"Failed to decrypt cookie: {e}")
                        continue
                
                # Convert datetime strings
                if data['expires']:
                    data['expires'] = datetime.fromisoformat(data['expires'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['last_used'] = datetime.fromisoformat(data['last_used'])
                
                # Remove database-specific fields
                del data['id']
                del data['encrypted']
                
                cookie = CookieData.from_dict(data)
                self.cookie_jar.add_cookie(cookie)
            
            conn.close()
            logger.info(f"Loaded {len(rows)} cookies from SQLite")
            
        except Exception as e:
            logger.error(f"Failed to load cookies from SQLite: {e}")
    
    async def _save_to_sqlite(self) -> None:
        """Save cookies to SQLite."""        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Clear existing cookies
            cursor.execute("DELETE FROM cookies")
            
            # Save current cookies
            for domain, domain_cookies in self.cookie_jar.cookies.items():
                for name, cookie in domain_cookies.items():
                    data = cookie.to_dict()
                    
                    # Encrypt sensitive cookies
                    encrypted = False
                    if self.cipher and self._should_encrypt_cookie(cookie):
                        try:
                            data['value'] = self.cipher.encrypt(data['value'].encode()).decode()
                            encrypted = True
                        except Exception as e:
                            logger.warning(f"Failed to encrypt cookie: {e}")
                    
                    cursor.execute("""                        INSERT OR REPLACE INTO cookies 
                        (domain, name, value, path, expires, max_age, secure, 
                         http_only, same_site, created_at, last_used, use_count, encrypted)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['domain'], data['name'], data['value'], data['path'],
                        data['expires'], data['max_age'], data['secure'],
                        data['http_only'], data['same_site'], data['created_at'],
                        data['last_used'], data['use_count'], encrypted
                    ))
            
            conn.commit()
            conn.close()
            
            cookie_count = self.cookie_jar.get_cookie_count()
            logger.info(f"Saved {cookie_count} cookies to SQLite")
            
        except Exception as e:
            logger.error(f"Failed to save cookies to SQLite: {e}")
    
    def _should_encrypt_cookie(self, cookie: CookieData) -> bool:
        """Determine if cookie should be encrypted."""        # Encrypt session tokens, auth cookies, etc.
        sensitive_patterns = [
            'session',
            'auth',
            'token',
            'csrf',
            'jwt',
            'oauth',
            'login'
        ]
        
        name_lower = cookie.name.lower()
        for pattern in sensitive_patterns:
            if pattern in name_lower:
                return True
        
        return False
    
    async def _persist_cookie(self, cookie: CookieData) -> None:
        """Persist single cookie immediately."""        if self.redis_client:
            await self._persist_cookie_redis(cookie)
        elif self.storage_path:
            await self._persist_cookie_sqlite(cookie)
    
    async def _persist_cookie_sqlite(self, cookie: CookieData) -> None:
        """Persist single cookie to SQLite."""        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            data = cookie.to_dict()
            
            # Encrypt if needed
            encrypted = False
            if self.cipher and self._should_encrypt_cookie(cookie):
                try:
                    data['value'] = self.cipher.encrypt(data['value'].encode()).decode()
                    encrypted = True
                except Exception as e:
                    logger.warning(f"Failed to encrypt cookie: {e}")
            
            cursor.execute("""                INSERT OR REPLACE INTO cookies 
                (domain, name, value, path, expires, max_age, secure, 
                 http_only, same_site, created_at, last_used, use_count, encrypted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['domain'], data['name'], data['value'], data['path'],
                data['expires'], data['max_age'], data['secure'],
                data['http_only'], data['same_site'], data['created_at'],
                data['last_used'], data['use_count'], encrypted
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to persist cookie to SQLite: {e}")
    
    async def cleanup_expired_cookies(self) -> int:
        """Clean up expired cookies and return count removed."""        initial_count = self.cookie_jar.get_cookie_count()
        self.cookie_jar._clean_expired_cookies()
        final_count = self.cookie_jar.get_cookie_count()
        
        removed_count = initial_count - final_count
        
        if removed_count > 0:
            await self.save_cookies()
            logger.info(f"Cleaned up {removed_count} expired cookies")
        
        return removed_count
    
    async def get_cookie_statistics(self) -> Dict:
        """Get cookie usage statistics."""        domains = self.cookie_jar.get_domains()
        total_cookies = self.cookie_jar.get_cookie_count()
        
        domain_stats = {}
        for domain in domains:
            domain_cookies = self.cookie_jar.cookies.get(domain, {})
            domain_stats[domain] = {
                'count': len(domain_cookies),
                'last_used': max(
                    (cookie.last_used for cookie in domain_cookies.values()),
                    default=datetime.min
                ),
                'total_uses': sum(cookie.use_count for cookie in domain_cookies.values())
            }
        
        return {
            'total_cookies': total_cookies,
            'total_domains': len(domains),
            'domain_stats': domain_stats,
            'storage_backend': 'redis' if self.redis_client else 'sqlite'
        }
    
    async def clear_domain_cookies(self, domain: str) -> None:
        """Clear cookies for specific domain."""        self.cookie_jar.clear_domain_cookies(domain)
        await self.save_cookies()
    
    async def clear_all_cookies(self) -> None:
        """Clear all cookies."""        self.cookie_jar.clear_all_cookies()
        await self.save_cookies()

# Cookie utilities
def parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    """Parse cookie string into name-value pairs."""    cookies = {}
    
    try:
        for pair in cookie_string.split(';'):
            if '=' in pair:
                name, value = pair.strip().split('=', 1)
                cookies[name] = value
    except Exception as e:
        logger.warning(f"Failed to parse cookie string: {e}")
    
    return cookies

def format_cookie_header(cookies: Dict[str, str]) -> str:
    """Format cookies into header string."""    return '; '.join(f"{name}={value}" for name, value in cookies.items())

def is_secure_cookie(cookie: CookieData) -> bool:
    """Check if cookie has secure attributes."""    return cookie.secure and cookie.http_only

def get_cookie_domain_level(domain: str) -> int:
    """Get domain level (number of dots + 1)."""    return domain.count('.') + 1

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL for cookie purposes."""    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""
