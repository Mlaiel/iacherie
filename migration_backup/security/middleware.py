#!/usr/bin/env python3
"""
🔒 SECURITY MIDDLEWARE
=====================

Security middleware for request validation and protection.
"""

import time
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class SecurityMiddleware:
    """Security middleware for request protection"""
    
    def __init__(self):
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.blocked_ips: set = set()
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    
    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming request for security threats"""
        
        client_ip = request_data.get("client_ip", "unknown")
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return {"allowed": False, "reason": "IP blocked"}
        
        # Check rate limiting
        if not self._check_rate_limit(client_ip):
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        # Validate input
        if not self._validate_input(request_data.get("data", {})):
            return {"allowed": False, "reason": "Invalid input detected"}
        
        return {"allowed": True, "headers": self.security_headers}
    
    def _check_rate_limit(self, client_ip: str, limit: int = 100) -> bool:
        """Check rate limiting for client IP"""
        now = datetime.now()
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Remove old requests
        cutoff_time = now - timedelta(minutes=1)
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(self.rate_limits[client_ip]) >= limit:
            return False
        
        self.rate_limits[client_ip].append(now)
        return True
    
    def _validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for malicious content"""
        
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',                # JavaScript injection
            r'on\w+\s*=',                 # Event handlers
            r'(?i)(union|select|insert|update|delete|drop)\s+',  # SQL injection
            r'\.\./',                     # Path traversal
        ]
        
        def check_value(value):
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    if re.search(pattern, value):
                        return False
            elif isinstance(value, dict):
                return all(check_value(v) for v in value.values())
            elif isinstance(value, list):
                return all(check_value(item) for item in value)
            return True
        
        return check_value(data)

# Global security middleware
security_middleware = SecurityMiddleware()
