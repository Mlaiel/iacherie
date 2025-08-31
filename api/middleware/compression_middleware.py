"""Asset Compression Middleware - Web Asset Optimization
Middleware for compressing and optimizing web assets (CSS, JS, images)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import gzip

import zlib
import io

from typing import Callable, List, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from starlette.responses import StreamingResponse

import logging

logger = logging.getLogger(__name__)


class AssetCompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for compressing static assets and API responses
    
    Features:
    - Multiple compression algorithms (gzip, deflate)
    - Content-type specific compression
    - Configurable compression levels
    - File size thresholds
    - Cache-friendly headers
    """
    
    def __init__(
        self,
        app,
        compression_level: int = 6,
        min_response_size: int = 1024,  # Only compress responses > 1KB
        compressible_types: List[str] = None,
        exclude_paths: List[str] = None,
        enable_gzip: bool = True,
        enable_deflate: bool = True
    ):
        super().__init__(app)
        self.compression_level = compression_level
        self.min_response_size = min_response_size
        self.enable_gzip = enable_gzip
        self.enable_deflate = enable_deflate
        self.exclude_paths = exclude_paths or []
        
        # Default compressible content types
        self.compressible_types = compressible_types or [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'text/xml',
            'text/plain',
            'application/x-javascript',
            'text/x-component',
            'text/x-json'
        ]
        
        # Compression statistics
        self.compressions_performed = 0
        self.total_bytes_saved = 0
        
        logger.info("Asset Compression Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response if appropriate"""
        
        response = await call_next(request)
        
        # Check if we should compress this response
        if not self._should_compress(request, response):
            return response
        
        # Get accepted encodings
        accept_encoding = request.headers.get('accept-encoding', '')
        
        # Choose compression method
        if self.enable_gzip and 'gzip' in accept_encoding:
            return await self._compress_response_gzip(response)
        elif self.enable_deflate and 'deflate' in accept_encoding:
            return await self._compress_response_deflate(response)
        
        return response
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """
Determine if response should be compressed"""
        
        # Check excluded paths
        for excluded_path in self.exclude_paths:
            if request.url.path.startswith(excluded_path):
                return False
        
        # Check if already compressed
        if response.headers.get('content-encoding'):
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in self.compressible_types:
            return False
        
        # Check response size
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) < self.min_response_size:
            return False
        
        return True
    
    async def _compress_response_gzip(self, response: Response) -> Response:
        """
Compress response using gzip"""
        
        try:
            # Get response body
            body = self._get_response_body(response)
            
            if not body or len(body) < self.min_response_size:
                return response
            
            # Compress with gzip
            compressed_body = gzip.compress(
                body.encode() if isinstance(body, str) else body,
                compresslevel=self.compression_level
            )
            
            # Update statistics
            self.compressions_performed += 1
            self.total_bytes_saved += len(body) - len(compressed_body)
            
            # Create new response with compressed body
            new_response = Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Update headers
            new_response.headers['content-encoding'] = 'gzip'
            new_response.headers['content-length'] = str(len(compressed_body))
            new_response.headers['vary'] = 'Accept-Encoding'
            
            return new_response
            
        except Exception as e:
            logger.warning(f"Failed to compress response with gzip: {e}")
            return response
    
    async def _compress_response_deflate(self, response: Response) -> Response:
        """Compress response using deflate"""
        
        try:
            # Get response body
            body = self._get_response_body(response)
            
            if not body or len(body) < self.min_response_size:
                return response
            
            # Compress with deflate
            compressed_body = zlib.compress(
                body.encode() if isinstance(body, str) else body,
                level=self.compression_level
            )
            
            # Update statistics
            self.compressions_performed += 1
            self.total_bytes_saved += len(body) - len(compressed_body)
            
            # Create new response with compressed body
            new_response = Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Update headers
            new_response.headers['content-encoding'] = 'deflate'
            new_response.headers['content-length'] = str(len(compressed_body))
            new_response.headers['vary'] = 'Accept-Encoding'
            
            return new_response
            
        except Exception as e:
            logger.warning(f"Failed to compress response with deflate: {e}")
            return response
    
    def _get_response_body(self, response: Response) -> Optional[bytes]:
        """Extract body from response"""
        
        if hasattr(response, 'body') and response.body:
            return response.body
        
        # For streaming responses, we can't easily compress
        if isinstance(response, StreamingResponse):
            return None
        
        return None
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """
Get compression performance statistics"""
        
        avg_savings = (
            self.total_bytes_saved / self.compressions_performed
            if self.compressions_performed > 0 else 0
        )
        
        return {
            "compressions_performed": self.compressions_performed,
            "total_bytes_saved": self.total_bytes_saved,
            "average_bytes_saved": round(avg_savings, 2),
            "compression_level": self.compression_level
        }


class StaticAssetOptimizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for optimizing static assets (CSS, JS minification, etc.)
    """
    
    def __init__(
        self,
        app,
        enable_css_minification: bool = True,
        enable_js_minification: bool = True,
        enable_html_minification: bool = True,
        static_paths: List[str] = None
    ):
        super().__init__(app)
        self.enable_css_minification = enable_css_minification
        self.enable_js_minification = enable_js_minification
        self.enable_html_minification = enable_html_minification
        self.static_paths = static_paths or ['/static/', '/assets/', '/public/']
        
        logger.info("Static Asset Optimization Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and optimize static assets"""
        
        response = await call_next(request)
        
        # Check if this is a static asset request
        if self._is_static_asset(request):
            return await self._optimize_asset(request, response)
        
        return response
    
    def _is_static_asset(self, request: Request) -> bool:
        """
Check if request is for a static asset"""
        
        path = request.url.path
        return any(path.startswith(static_path) for static_path in self.static_paths)
    
    async def _optimize_asset(self, request: Request, response: Response) -> Response:
        """
Optimize static asset based on type"""
        
        content_type = response.headers.get('content-type', '').split(';')[0]
        
        if content_type == 'text/css' and self.enable_css_minification:
            return self._minify_css(response)
        elif content_type in ['application/javascript', 'text/javascript'] and self.enable_js_minification:
            return self._minify_javascript(response)
        elif content_type == 'text/html' and self.enable_html_minification:
            return self._minify_html(response)
        
        return response
    
    def _minify_css(self, response: Response) -> Response:
        """
Basic CSS minification"""
        
        try:
            body = self._get_response_body_as_string(response)
            if not body:
                return response
            
            # Basic CSS minification
            # Remove comments
            import re
            minified = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)
            
            # Remove extra whitespace
            minified = re.sub(r'\s+', ' ', minified)
            minified = re.sub(r';\s*}', '}', minified)
            minified = re.sub(r':\s+', ':', minified)
            minified = re.sub(r';\s+', ';', minified)
            minified = minified.strip()
            
            # Create new response
            new_response = Response(
                content=minified,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            new_response.headers['content-length'] = str(len(minified))
            
            return new_response
            
        except Exception as e:
            logger.warning(f"Failed to minify CSS: {e}")
            return response
    
    def _minify_javascript(self, response: Response) -> Response:
        """Basic JavaScript minification"""
        
        try:
            body = self._get_response_body_as_string(response)
            if not body:
                return response
            
            # Basic JS minification
            import re
            
            # Remove single-line comments (but preserve URLs)
            minified = re.sub(r'(?<!:)//.*?$', '', body, flags=re.MULTILINE)
            
            # Remove multi-line comments
            minified = re.sub(r'/\*.*?\*/', '', minified, flags=re.DOTALL)
            
            # Remove extra whitespace
            minified = re.sub(r'\s+', ' ', minified)
            minified = minified.strip()
            
            # Create new response
            new_response = Response(
                content=minified,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            new_response.headers['content-length'] = str(len(minified))
            
            return new_response
            
        except Exception as e:
            logger.warning(f"Failed to minify JavaScript: {e}")
            return response
    
    def _minify_html(self, response: Response) -> Response:
        """Basic HTML minification"""
        
        try:
            body = self._get_response_body_as_string(response)
            if not body:
                return response
            
            # Basic HTML minification
            import re
            
            # Remove HTML comments (but preserve conditional comments)
            minified = re.sub(r'<!--(?!\[if\s).*?-->', '', body, flags=re.DOTALL)
            
            # Remove extra whitespace between tags
            minified = re.sub(r'>\s+<', '><', minified)
            
            # Remove leading/trailing whitespace on lines
            minified = '\n'.join(line.strip() for line in minified.split('\n'))
            
            # Remove empty lines
            minified = re.sub(r'\n\s*\n', '\n', minified)
            
            # Create new response
            new_response = Response(
                content=minified,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            new_response.headers['content-length'] = str(len(minified))
            
            return new_response
            
        except Exception as e:
            logger.warning(f"Failed to minify HTML: {e}")
            return response
    
    def _get_response_body_as_string(self, response: Response) -> Optional[str]:
        """Get response body as string"""
        
        if hasattr(response, 'body') and response.body:
            if isinstance(response.body, bytes):
                return response.body.decode('utf-8')
            elif isinstance(response.body, str):
                return response.body
        
        return None