"""
HTTP/2 Compression Configuration with Asset Optimization
Advanced compression and asset optimization for high performance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import gzip
import brotli
import zlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import mimetypes
import hashlib
import json
import time


@dataclass
class CompressionConfig:
    """Configuration for HTTP compression"""
    
    # General compression settings
    enable_gzip: bool = True
    enable_brotli: bool = True
    enable_deflate: bool = True
    
    # Compression levels (1-9 for gzip, 1-11 for brotli)
    gzip_level: int = 6
    brotli_level: int = 6
    deflate_level: int = 6
    
    # Minimum file size to compress (bytes)
    min_compress_size: int = 1024  # 1KB
    max_compress_size: int = 10 * 1024 * 1024  # 10MB
    
    # MIME types to compress
    compressible_types: List[str] = field(default_factory=lambda: [
        'text/html',
        'text/css',
        'text/javascript',
        'text/plain',
        'text/xml',
        'text/csv',
        'application/javascript',
        'application/json',
        'application/xml',
        'application/rss+xml',
        'application/atom+xml',
        'image/svg+xml',
        'application/font-woff',
        'application/font-woff2',
        'font/woff',
        'font/woff2',
        'font/opentype',
        'application/vnd.ms-fontobject'
    ])
    
    # Types to never compress
    non_compressible_types: List[str] = field(default_factory=lambda: [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'audio/mpeg',
        'audio/ogg',
        'video/mp4',
        'video/mpeg',
        'video/webm',
        'application/pdf',
        'application/zip',
        'application/gzip',
        'application/x-rar-compressed',
        'application/x-7z-compressed'
    ])


@dataclass
class AssetOptimizationConfig:
    """Configuration for asset optimization"""
    
    # Asset types to optimize
    optimize_images: bool = True
    optimize_css: bool = True
    optimize_js: bool = True
    optimize_fonts: bool = True
    
    # Image optimization
    image_quality: int = 85  # JPEG quality
    webp_quality: int = 80
    enable_webp_conversion: bool = True
    enable_avif_conversion: bool = False
    
    # CSS optimization
    minify_css: bool = True
    remove_css_comments: bool = True
    combine_css_files: bool = True
    
    # JavaScript optimization
    minify_js: bool = True
    remove_js_comments: bool = True
    combine_js_files: bool = True
    
    # Font optimization
    subset_fonts: bool = True
    convert_to_woff2: bool = True
    
    # Caching
    enable_file_hashing: bool = True
    cache_busting: bool = True
    
    # Output directories
    output_dir: str = "static/optimized"
    cache_dir: str = "cache/assets"


class CompressionMiddleware:
    """HTTP compression middleware"""
    
    def __init__(self, config: CompressionConfig):
        self.config = config
        self.compression_cache: Dict[str, bytes] = {}
        
    def should_compress(self, content_type: str, content_length: int) -> bool:
        """Determine if content should be compressed"""
        
        # Check size limits
        if content_length < self.config.min_compress_size:
            return False
        
        if content_length > self.config.max_compress_size:
            return False
        
        # Check MIME type
        if content_type in self.config.non_compressible_types:
            return False
        
        # Check if type is compressible
        for compressible_type in self.config.compressible_types:
            if content_type.startswith(compressible_type):
                return True
        
        return False
    
    def get_best_encoding(self, accept_encoding: str) -> Optional[str]:
        """Get the best compression encoding based on client support"""
        if not accept_encoding:
            return None
        
        accept_encoding = accept_encoding.lower()
        
        # Prioritize Brotli (best compression)
        if self.config.enable_brotli and 'br' in accept_encoding:
            return 'br'
        
        # Then gzip (widely supported)
        if self.config.enable_gzip and 'gzip' in accept_encoding:
            return 'gzip'
        
        # Finally deflate
        if self.config.enable_deflate and 'deflate' in accept_encoding:
            return 'deflate'
        
        return None
    
    def compress_content(self, content: bytes, encoding: str) -> bytes:
        """Compress content using specified encoding"""
        
        # Generate cache key
        cache_key = f"{encoding}:{hashlib.md5(content).hexdigest()}"
        
        # Check cache first
        if cache_key in self.compression_cache:
            return self.compression_cache[cache_key]
        
        compressed = None
        
        if encoding == 'br' and self.config.enable_brotli:
            compressed = brotli.compress(content, quality=self.config.brotli_level)
        
        elif encoding == 'gzip' and self.config.enable_gzip:
            compressed = gzip.compress(content, compresslevel=self.config.gzip_level)
        
        elif encoding == 'deflate' and self.config.enable_deflate:
            compressed = zlib.compress(content, level=self.config.deflate_level)
        
        if compressed:
            # Cache the result (with size limit)
            if len(self.compression_cache) < 1000:  # Limit cache size
                self.compression_cache[cache_key] = compressed
            return compressed
        
        return content
    
    async def process_response(self, content: bytes, content_type: str, 
                             accept_encoding: str) -> tuple[bytes, Dict[str, str]]:
        """Process response for compression"""
        
        headers = {}
        
        if not self.should_compress(content_type, len(content)):
            return content, headers
        
        encoding = self.get_best_encoding(accept_encoding)
        if not encoding:
            return content, headers
        
        compressed_content = self.compress_content(content, encoding)
        
        # Add compression headers
        headers['Content-Encoding'] = encoding
        headers['Content-Length'] = str(len(compressed_content))
        headers['Vary'] = 'Accept-Encoding'
        
        return compressed_content, headers


class AssetOptimizer:
    """Asset optimization for static files"""
    
    def __init__(self, config: AssetOptimizationConfig):
        self.config = config
        self.optimization_cache: Dict[str, str] = {}
        
        # Ensure output directories exist
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for file content"""
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()[:8]
    
    def optimize_css(self, css_content: str) -> str:
        """Optimize CSS content"""
        if not self.config.minify_css:
            return css_content
        
        # Simple CSS minification
        optimized = css_content
        
        if self.config.remove_css_comments:
            # Remove comments
            import re
            optimized = re.sub(r'/\*.*?\*/', '', optimized, flags=re.DOTALL)
        
        if self.config.minify_css:
            # Remove unnecessary whitespace
            optimized = re.sub(r'\s+', ' ', optimized)
            optimized = re.sub(r';\s*}', '}', optimized)
            optimized = re.sub(r'{\s*', '{', optimized)
            optimized = re.sub(r';\s*', ';', optimized)
            optimized = optimized.strip()
        
        return optimized
    
    def optimize_js(self, js_content: str) -> str:
        """Optimize JavaScript content"""
        if not self.config.minify_js:
            return js_content
        
        # Simple JS minification (for production, use tools like terser)
        optimized = js_content
        
        if self.config.remove_js_comments:
            # Remove single-line comments
            import re
            optimized = re.sub(r'//.*$', '', optimized, flags=re.MULTILINE)
            # Remove multi-line comments
            optimized = re.sub(r'/\*.*?\*/', '', optimized, flags=re.DOTALL)
        
        return optimized
    
    def process_file(self, file_path: str) -> str:
        """Process and optimize a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check cache
        file_key = str(file_path)
        file_hash = self.get_file_hash(file_path)
        cache_key = f"{file_key}:{file_hash}"
        
        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Optimize based on file type
        optimized_content = content
        suffix = file_path.suffix.lower()
        
        if suffix == '.css' and self.config.optimize_css:
            optimized_content = self.optimize_css(content)
        
        elif suffix == '.js' and self.config.optimize_js:
            optimized_content = self.optimize_js(content)
        
        # Generate output filename
        if self.config.enable_file_hashing:
            output_name = f"{file_path.stem}.{file_hash}{file_path.suffix}"
        else:
            output_name = file_path.name
        
        output_path = Path(self.config.output_dir) / output_name
        
        # Write optimized file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        # Cache the result
        self.optimization_cache[cache_key] = str(output_path)
        
        return str(output_path)
    
    def generate_asset_manifest(self) -> Dict[str, str]:
        """Generate asset manifest for cache busting"""
        manifest = {}
        
        for original_path, optimized_path in self.optimization_cache.items():
            original_file = original_path.split(':')[0]
            manifest[original_file] = optimized_path
        
        manifest_path = Path(self.config.output_dir) / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest


class HTTP2Config:
    """HTTP/2 configuration for NGINX/server"""
    
    @staticmethod
    def generate_nginx_config(compression_config: CompressionConfig) -> str:
        """Generate NGINX configuration for HTTP/2 and compression"""
        
        # MIME types for compression
        compressible_types = ' '.join(compression_config.compressible_types)
        
        config = f"""
# HTTP/2 and Compression Configuration
# Generated for IA-Influencer Platform

# Enable HTTP/2
listen 443 ssl http2;
listen [::]:443 ssl http2;

# Compression settings
gzip on;
gzip_vary on;
gzip_min_length {compression_config.min_compress_size};
gzip_comp_level {compression_config.gzip_level};
gzip_types {compressible_types};

# Brotli compression
brotli on;
brotli_comp_level {compression_config.brotli_level};
brotli_min_length {compression_config.min_compress_size};
brotli_types {compressible_types};

# HTTP/2 push for critical resources
location = /index.html {{
    http2_push /static/css/critical.css;
    http2_push /static/js/app.js;
    http2_push /static/fonts/main.woff2;
}}

# Static asset optimization
location /static/ {{
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Compression for specific file types
    location ~* \.(js|css|json|xml|txt)$ {{
        gzip_static on;
        brotli_static on;
    }}
}}

# API responses compression
location /api/ {{
    gzip on;
    gzip_types application/json application/xml text/plain;
    brotli on;
    brotli_types application/json application/xml text/plain;
}}

# Image optimization
location ~* \.(jpg|jpeg|png|gif|webp|avif)$ {{
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept";
    
    # WebP fallback
    location ~* \.(jpg|jpeg|png)$ {{
        try_files $uri$webp_suffix $uri =404;
    }}
}}

# Font optimization
location ~* \.(woff|woff2|ttf|otf|eot)$ {{
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Access-Control-Allow-Origin "*";
}}
"""
        
        return config.strip()
    
    @staticmethod
    def generate_apache_config(compression_config: CompressionConfig) -> str:
        """Generate Apache configuration for HTTP/2 and compression"""
        
        config = f"""
# HTTP/2 and Compression Configuration for Apache
# Generated for IA-Influencer Platform

# Enable HTTP/2
Protocols h2 http/1.1

# Load required modules
LoadModule deflate_module modules/mod_deflate.so
LoadModule brotli_module modules/mod_brotli.so
LoadModule http2_module modules/mod_http2.so

# Compression settings
<IfModule mod_deflate.c>
    SetOutputFilter DEFLATE
    SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png|zip|gz|bz2)$ no-gzip dont-vary
    
    # Compress specific MIME types
    AddOutputFilterByType DEFLATE {' '.join(compression_config.compressible_types)}
    
    DeflateCompressionLevel {compression_config.deflate_level}
    DeflateFilterNote Input instream
    DeflateFilterNote Output outstream
    DeflateFilterNote Ratio ratio
</IfModule>

# Brotli compression
<IfModule mod_brotli.c>
    BrotliCompressionQuality {compression_config.brotli_level}
    BrotliFilterNote Input instream
    BrotliFilterNote Output outstream
    BrotliFilterNote Ratio ratio
    
    # Compress specific MIME types
    AddOutputFilterByType BROTLI_COMPRESS {' '.join(compression_config.compressible_types)}
</IfModule>

# Static file optimization
<Directory "/var/www/html/static">
    # Cache headers
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    # Vary header for compression
    Header append Vary Accept-Encoding
</Directory>

# API compression
<LocationMatch "^/api/">
    SetOutputFilter DEFLATE
    SetOutputFilter BROTLI_COMPRESS
</LocationMatch>
"""
        
        return config.strip()


# Example usage and integration
class PerformanceOptimizer:
    """Main class for performance optimization"""
    
    def __init__(self, compression_config: CompressionConfig = None,
                 asset_config: AssetOptimizationConfig = None):
        self.compression_config = compression_config or CompressionConfig()
        self.asset_config = asset_config or AssetOptimizationConfig()
        
        self.compression_middleware = CompressionMiddleware(self.compression_config)
        self.asset_optimizer = AssetOptimizer(self.asset_config)
    
    async def optimize_response(self, content: bytes, content_type: str,
                              accept_encoding: str) -> tuple[bytes, Dict[str, str]]:
        """Optimize HTTP response"""
        return await self.compression_middleware.process_response(
            content, content_type, accept_encoding
        )
    
    def optimize_static_assets(self, asset_dir: str) -> Dict[str, str]:
        """Optimize all static assets in directory"""
        asset_path = Path(asset_dir)
        manifest = {}
        
        for file_path in asset_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.css', '.js']:
                try:
                    optimized_path = self.asset_optimizer.process_file(file_path)
                    manifest[str(file_path)] = optimized_path
                except Exception as e:
                    print(f"Error optimizing {file_path}: {e}")
        
        return manifest
    
    def generate_server_configs(self) -> Dict[str, str]:
        """Generate server configuration files"""
        return {
            'nginx': HTTP2Config.generate_nginx_config(self.compression_config),
            'apache': HTTP2Config.generate_apache_config(self.compression_config)
        }


# FastAPI integration example
def create_compression_middleware():
    """Create compression middleware for FastAPI"""
    from fastapi import Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    
    class FastAPICompressionMiddleware(BaseHTTPMiddleware):
        def __init__(self, app, compression_config: CompressionConfig = None):
            super().__init__(app)
            self.optimizer = PerformanceOptimizer(compression_config)
        
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            
            # Get response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            
            # Optimize response
            accept_encoding = request.headers.get('accept-encoding', '')
            content_type = response.headers.get('content-type', '')
            
            optimized_body, compression_headers = await self.optimizer.optimize_response(
                body, content_type, accept_encoding
            )
            
            # Update response
            for key, value in compression_headers.items():
                response.headers[key] = value
            
            # Return new response with optimized body
            return Response(
                content=optimized_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )
    
    return FastAPICompressionMiddleware


if __name__ == "__main__":
    # Example usage
    optimizer = PerformanceOptimizer()
    
    # Generate server configs
    configs = optimizer.generate_server_configs()
    print("NGINX Config:")
    print(configs['nginx'])
    
    print("\nApache Config:")
    print(configs['apache'])