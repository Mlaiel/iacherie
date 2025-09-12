"""🔍 Evidence Collector
===================

Automated evidence collection system for content protection violations.
Captures screenshots, metadata, and digital fingerprints as legal proof.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json
import os
import io
from urllib.parse import urlparse

# Optional aiohttp with fallback
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    class AioHttpFallback:
        class ClientSession:
            def __init__(self, *args, **kwargs): pass
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def get(self, url, **kwargs):
                return self.Response()
            async def post(self, url, **kwargs):
                return self.Response()
        class Response:
            def __init__(self):
                self.status = 200
                self.headers = {}
            async def text(self): return ""
            async def json(self): return {}
            async def read(self): return b""
    aiohttp = AioHttpFallback()

# Optional aiofiles with fallback
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    class AioFilesFallback:
        @staticmethod
        def open(file, mode='r', **kwargs):
            return open(file, mode, **kwargs)
    aiofiles = AioFilesFallback()

# Optional selenium with fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    class WebDriverFallback:
        class Chrome:
            def __init__(self, *args, **kwargs): pass
            def get(self, url): pass
            def quit(self): pass
            def find_element(self, *args): 
                return self.Element()
            def save_screenshot(self, path): pass
        class Options:
            def add_argument(self, arg): pass
        class Element:
            def screenshot(self, path): pass
    webdriver = WebDriverFallback()
    Options = WebDriverFallback.Options
    By = None
    WebDriverWait = None
    EC = None

# Optional PIL with fallback
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
    PIL_Image = Image.Image  # Store the class for type hints
except ImportError:
    PIL_AVAILABLE = False
    class PILFallback:
        class Image:
            @staticmethod
            def open(path): return PILFallback.Image()
            def save(self, path): pass
            # Add Image class for type hints
            class Image:
                pass
        class ImageDraw:
            @staticmethod
            def Draw(img): return PILFallback.ImageDraw()
            def text(self, *args, **kwargs): pass
        class ImageFont:
            @staticmethod
            def truetype(*args, **kwargs): return None
    Image, ImageDraw, ImageFont = PILFallback.Image, PILFallback.ImageDraw, PILFallback.ImageFont
    PIL_Image = Image.Image  # For type hints

# Optional cv2 with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    class CV2Fallback:
        @staticmethod
        def imread(path): return []
        @staticmethod
        def imwrite(path, img): pass
    cv2 = CV2Fallback()

# Optional numpy with fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    class NumpyFallback:
        def array(self, data): return data
        def zeros(self, shape): return [0] * (shape if isinstance(shape, int) else shape[0])
    np = NumpyFallback()

# Optional pydantic with fallback
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    def Field(*args, **kwargs): return None

from ..models.alert_models import Alert

# Try to import evidence models with fallback
try:
    from ..models.evidence_models import Evidence, EvidenceType, EvidenceStatus
    EVIDENCE_MODELS_AVAILABLE = True
except ImportError:
    EVIDENCE_MODELS_AVAILABLE = False
    # Create fallback classes
    class Evidence:
        def __init__(self, *args, **kwargs): pass
    class EvidenceType:
        def __init__(self, *args, **kwargs): pass
    class EvidenceStatus:
        def __init__(self, *args, **kwargs): pass

# Core imports with fallbacks
try:
    from ...core.config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    class SettingsFallback:
        def __getattr__(self, name): return None
    settings = SettingsFallback()

try:
    try:
    from ...core.database import get_async_session
except ImportError:
    async def get_async_session(): return None
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def get_async_session(): return None

try:
    from ...core.storage import StorageManager
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    class StorageManager:
        def __init__(self, *args, **kwargs): pass

logger = logging.getLogger(__name__)

class EvidenceCollectionType(str, Enum):
    """
Types of evidence collection."""

    SCREENSHOT = "screenshot"
    VIDEO_CAPTURE = "video_capture"
    METADATA_EXTRACTION = "metadata_extraction"
    SOURCE_CODE = "source_code"
    NETWORK_TRACE = "network_trace"
    DIGITAL_FINGERPRINT = "digital_fingerprint"
    LEGAL_NOTICE = "legal_notice"

class CollectionStatus(str, Enum):
    """Evidence collection status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class EvidenceConfig:
    """Evidence collection configuration."""
    screenshot_quality: int = 95
    screenshot_format: str = "PNG"
    video_duration_seconds: int = 30
    video_quality: str = "720p"
    max_file_size_mb: int = 100
    watermark_enabled: bool = True
    timestamp_enabled: bool = True
    collection_timeout_seconds: int = 120
    parallel_collections: int = 3

@dataclass
class CollectionResult:
    """Result of evidence collection."""
    success: bool
    evidence_id: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    collection_time: Optional[datetime] = None

class WebDriverManager:
    """
Manages headless web drivers for evidence collection."""
    
    def __init__(self, config: EvidenceConfig):
        self.config = config
        self._driver_pool: List[webdriver.Chrome] = []
        self._pool_lock = asyncio.Lock()
        self._max_drivers = config.parallel_collections
    
    async def get_driver(self) -> webdriver.Chrome:
        """
Get a web driver from the pool."""
        async with self._pool_lock:
            if self._driver_pool:
                return self._driver_pool.pop()
            
            return self._create_driver()
    
    async def return_driver(self, driver: webdriver.Chrome) -> None:
        """
Return a web driver to the pool."""
        async with self._pool_lock:
            if len(self._driver_pool) < self._max_drivers:
                self._driver_pool.append(driver)
            else:
                driver.quit()
    
    def _create_driver(self) -> webdriver.Chrome:
        """
Create a new headless Chrome driver."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        return webdriver.Chrome(options=options)
    
    async def cleanup(self) -> None:
        """Clean up all drivers."""
        async with self._pool_lock:
            for driver in self._driver_pool:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error("Failed to quit driver: %s", str(e))
            self._driver_pool.clear()

class ScreenshotCollector:
    """Collects screenshot evidence with watermarking and metadata."""
    
    def __init__(self, config: EvidenceConfig, driver_manager: WebDriverManager):
        self.config = config
        self.driver_manager = driver_manager
    
    async def collect_screenshot(
        self,
        url: str,
        alert: Alert,
        evidence_path: str
    ) -> CollectionResult:
        """
Collect screenshot evidence from URL."""
        try:
            driver = await self.driver_manager.get_driver()
            
            try:
                # Navigate to URL
                driver.get(url)
                
                # Wait for page load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Take screenshot
                screenshot_data = driver.get_screenshot_as_png()
                
                # Process screenshot
                processed_image = await self._process_screenshot(
                    screenshot_data,
                    alert,
                    url
                )
                
                # Save to file
                file_path = f"{evidence_path}/screenshot_{alert.id}_{int(datetime.utcnow().timestamp())}.png"
                await self._save_image(processed_image, file_path)
                
                # Calculate checksum
                checksum = await self._calculate_checksum(file_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Collect metadata
                metadata = await self._collect_page_metadata(driver, url)
                
                return CollectionResult(
                    success=True,
                    file_path=file_path,
                    file_size=file_size,
                    checksum=checksum,
                    metadata=metadata,
                    collection_time=datetime.utcnow()
                )
                
            finally:
                await self.driver_manager.return_driver(driver)
                
        except Exception as e:
            logger.error("Failed to collect screenshot: %s", str(e))
            return CollectionResult(
                success=False,
                error_message=str(e)
            )
    
    async def _process_screenshot(
        self,
        screenshot_data: bytes,
        alert: Alert,
        url: str
    ) -> PIL_Image:  # Use our fallback-compatible type hint
        """Process screenshot with watermark and timestamp."""
        # Convert to PIL Image
        image = Image.open(io.BytesIO(screenshot_data))
        
        if self.config.watermark_enabled:
            # Add watermark
            image = await self._add_watermark(image, alert, url)
        
        if self.config.timestamp_enabled:
            # Add timestamp
            image = await self._add_timestamp(image)
        
        return image
    
    async def _add_watermark(self, image: Image.Image, alert: Alert, url: str) -> Image.Image:
        """
Add watermark to screenshot."""
        draw = ImageDraw.Draw(image)
        
        # Watermark text
        watermark_text = f"IA Influencer Agent - Evidence Collection\nAlert: {alert.id}\nURL: {url}\nTimestamp: {datetime.utcnow().isoformat()}"
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # Add semi-transparent background
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position in bottom right
        x = image.width - text_width - 20
        y = image.height - text_height - 20
        
        # Draw background rectangle
        draw.rectangle(
            [x - 10, y - 5, x + text_width + 10, y + text_height + 5],
            fill=(0, 0, 0, 128)
        )
        
        # Draw text
        draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
        
        return image
    
    async def _add_timestamp(self, image: Image.Image) -> Image.Image:
        """Add timestamp to screenshot."""
        draw = ImageDraw.Draw(image)
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Position in top left
        draw.text((10, 10), timestamp, fill=(255, 0, 0), font=font)
        
        return image
    
    async def _save_image(self, image: Image.Image, file_path: str) -> None:
        """Save image to file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save with specified quality
        image.save(
            file_path,
            format=self.config.screenshot_format,
            quality=self.config.screenshot_quality,
            optimize=True
        )
    
    async def _collect_page_metadata(self, driver: webdriver.Chrome, url: str) -> Dict[str, Any]:
        """
Collect page metadata."""
        metadata = {
            "url": url,
            "title": driver.title,
            "page_source_hash": hashlib.sha256(driver.page_source.encode()).hexdigest(),
            "viewport_size": driver.get_window_size(),
            "user_agent": driver.execute_script("return navigator.userAgent;"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Collect meta tags
        try:
            meta_tags = driver.find_elements(By.TAG_NAME, "meta")
            metadata["meta_tags"] = {}
            
            for meta in meta_tags:
                name = meta.get_attribute("name") or meta.get_attribute("property")
                content = meta.get_attribute("content")
                
                if name and content:
                    metadata["meta_tags"][name] = content
        except Exception as e:
            logger.warning("Failed to collect meta tags: %s", str(e))
        
        return metadata
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

class VideoCollector:
    """Collects video evidence of violations."""
    
    def __init__(self, config: EvidenceConfig, driver_manager: WebDriverManager):
        self.config = config
        self.driver_manager = driver_manager
    
    async def collect_video(
        self,
        url: str,
        alert: Alert,
        evidence_path: str
    ) -> CollectionResult:
        """
Collect video evidence from URL."""
        try:
            # For now, implement as series of screenshots
            # In production, would use screen recording tools
            
            screenshots = []
            driver = await self.driver_manager.get_driver()
            
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Capture screenshots over time
                for i in range(self.config.video_duration_seconds):
                    screenshot_data = driver.get_screenshot_as_png()
                    screenshots.append(screenshot_data)
                    await asyncio.sleep(1)
                
                # Create video from screenshots (simplified)
                video_path = f"{evidence_path}/video_{alert.id}_{int(datetime.utcnow().timestamp())}.mp4"
                await self._create_video_from_screenshots(screenshots, video_path)
                
                # Calculate checksum
                checksum = await self._calculate_checksum(video_path)
                file_size = os.path.getsize(video_path)
                
                return CollectionResult(
                    success=True,
                    file_path=video_path,
                    file_size=file_size,
                    checksum=checksum,
                    collection_time=datetime.utcnow()
                )
                
            finally:
                await self.driver_manager.return_driver(driver)
                
        except Exception as e:
            logger.error("Failed to collect video: %s", str(e))
            return CollectionResult(
                success=False,
                error_message=str(e)
            )
    
    async def _create_video_from_screenshots(
        self,
        screenshots: List[bytes],
        output_path: str
    ) -> None:
        """Create video from screenshot frames."""
        if not screenshots:
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert first screenshot to get dimensions
        first_image = Image.open(io.BytesIO(screenshots[0]))
        width, height = first_image.size
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 1.0, (width, height))
        
        try:
            for screenshot_data in screenshots:
                # Convert PIL to OpenCV format
                image = Image.open(io.BytesIO(screenshot_data))
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Write frame
                out.write(cv_image)
        finally:
            out.release()
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """
Calculate file checksum."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

class MetadataCollector:
    """Collects detailed metadata evidence."""
    
    def __init__(self, config: EvidenceConfig):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def collect_metadata(
        self,
        url: str,
        alert: Alert,
        evidence_path: str
    ) -> CollectionResult:
        """
Collect comprehensive metadata."""
        try:
            metadata = {}
            
            # HTTP headers
            metadata["http_headers"] = await self._collect_http_headers(url)
            
            # DNS information
            metadata["dns_info"] = await self._collect_dns_info(url)
            
            # WHOIS information
            metadata["whois_info"] = await self._collect_whois_info(url)
            
            # SSL certificate info
            metadata["ssl_info"] = await self._collect_ssl_info(url)
            
            # Social media metadata
            metadata["social_meta"] = await self._collect_social_metadata(url)
            
            # Save metadata to file
            metadata_path = f"{evidence_path}/metadata_{alert.id}_{int(datetime.utcnow().timestamp())}.json"
            await self._save_metadata(metadata, metadata_path)
            
            checksum = await self._calculate_checksum(metadata_path)
            file_size = os.path.getsize(metadata_path)
            
            return CollectionResult(
                success=True,
                file_path=metadata_path,
                file_size=file_size,
                checksum=checksum,
                metadata=metadata,
                collection_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Failed to collect metadata: %s", str(e))
            return CollectionResult(
                success=False,
                error_message=str(e)
            )
    
    async def _collect_http_headers(self, url: str) -> Dict[str, Any]:
        """Collect HTTP headers."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    return dict(response.headers)
        except Exception as e:
            logger.warning("Failed to collect HTTP headers: %s", str(e))
            return {}
    
    async def _collect_dns_info(self, url: str) -> Dict[str, Any]:
        """Collect DNS information."""
        try:
            import socket
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc
            
            ip_addresses = socket.gethostbyname_ex(hostname)[2]
            
            return {
                "hostname": hostname,
                "ip_addresses": ip_addresses,
                "resolved_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.warning("Failed to collect DNS info: %s", str(e))
            return {}
    
    async def _collect_whois_info(self, url: str) -> Dict[str, Any]:
        """Collect WHOIS information."""
        try:
            # Would implement WHOIS lookup
            # For now, return placeholder
            return {
                "whois_data": "Not implemented",
                "queried_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.warning("Failed to collect WHOIS info: %s", str(e))
            return {}
    
    async def _collect_ssl_info(self, url: str) -> Dict[str, Any]:
        """Collect SSL certificate information."""
        try:
            import ssl
            import socket
            from urllib.parse import urlparse
            
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc
            port = 443
            
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        "subject": dict(x[0] for x in cert['subject']),
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "version": cert['version'],
                        "serial_number": cert['serialNumber'],
                        "not_before": cert['notBefore'],
                        "not_after": cert['notAfter'],
                        "collected_at": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.warning("Failed to collect SSL info: %s", str(e))
            return {}
    
    async def _collect_social_metadata(self, url: str) -> Dict[str, Any]:
        """Collect social media metadata."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html_content = await response.text()
                    
                    # Parse social media meta tags
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    social_meta = {}
                    
                    # Open Graph tags
                    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
                    for tag in og_tags:
                        property_name = tag.get('property')
                        content = tag.get('content')
                        if property_name and content:
                            social_meta[property_name] = content
                    
                    # Twitter Card tags
                    twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
                    for tag in twitter_tags:
                        name = tag.get('name')
                        content = tag.get('content')
                        if name and content:
                            social_meta[name] = content
                    
                    return social_meta
                    
        except Exception as e:
            logger.warning("Failed to collect social metadata: %s", str(e))
            return {}
    
    async def _save_metadata(self, metadata: Dict[str, Any], file_path: str) -> None:
        """Save metadata to JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2, default=str))
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """
Calculate file checksum."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

class EvidenceCollector:
    """
    Main evidence collection orchestrator.
    """
    
    def __init__(
        self,
        config: EvidenceConfig,
        storage_manager: StorageManager
    ):
        self.config = config
        self.storage_manager = storage_manager
        
        # Initialize collectors
        self.driver_manager = WebDriverManager(config)
        self.screenshot_collector = ScreenshotCollector(config, self.driver_manager)
        self.video_collector = VideoCollector(config, self.driver_manager)
        self.metadata_collector = MetadataCollector(config)
        
        # Collection tracking
        self._active_collections: Dict[str, CollectionStatus] = {}
        self._collection_queue: asyncio.Queue = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._is_running = False
        
        logger.info("EvidenceCollector initialized")

    async def start(self) -> None:
        """Start evidence collection service."""
        if self._is_running:
            return
            
        self._is_running = True
        
        # Start collection workers
        for i in range(self.config.parallel_collections):
            worker = asyncio.create_task(self._collection_worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info("EvidenceCollector started with %d workers", len(self._workers))

    async def stop(self) -> None:
        """Stop evidence collection service."""
        self._is_running = False
        
        # Wait for queue to empty
        await self._collection_queue.join()
        
        # Cancel workers
        for worker in self._workers:
            worker.cancel()
        
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        # Cleanup drivers
        await self.driver_manager.cleanup()
        
        logger.info("EvidenceCollector stopped")

    async def collect_evidence(self, alert: Alert) -> Dict[str, CollectionResult]:
        """
        Collect comprehensive evidence for an alert.
        
        Args:
            alert: Alert requiring evidence collection
            
        Returns:
            Dictionary of collection results by evidence type
        """
        try:
            collection_id = str(uuid4())
            evidence_path = f"evidence/{alert.user_id}/{alert.id}/{collection_id}"
            
            # Create evidence directory
            full_evidence_path = os.path.join(settings.STORAGE_PATH, evidence_path)
            os.makedirs(full_evidence_path, exist_ok=True)
            
            results = {}
            
            # Determine what evidence to collect based on alert
            collection_types = await self._determine_collection_types(alert)
            
            # Collect evidence in parallel
            collection_tasks = []
            
            for collection_type in collection_types:
                task = asyncio.create_task(
                    self._collect_evidence_type(
                        collection_type,
                        alert,
                        full_evidence_path
                    )
                )
                collection_tasks.append((collection_type, task))
            
            # Wait for all collections to complete
            for collection_type, task in collection_tasks:
                try:
                    result = await asyncio.wait_for(
                        task,
                        timeout=self.config.collection_timeout_seconds
                    )
                    results[collection_type.value] = result
                except asyncio.TimeoutError:
                    results[collection_type.value] = CollectionResult(
                        success=False,
                        error_message="Collection timeout"
                    )
                except Exception as e:
                    results[collection_type.value] = CollectionResult(
                        success=False,
                        error_message=str(e)
                    )
            
            # Store evidence records in database
            await self._store_evidence_records(alert.id, collection_id, results)
            
            logger.info(
                "Evidence collection completed for alert %s: %d/%d successful",
                alert.id,
                sum(1 for r in results.values() if r.success),
                len(results)
            )
            
            return results
            
        except Exception as e:
            logger.error("Failed to collect evidence for alert %s: %s", alert.id, str(e))
            return {}

    async def get_evidence_summary(self, alert_id: str) -> Dict[str, Any]:
        """Get evidence collection summary for an alert."""
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(Evidence).where(Evidence.alert_id == alert_id)
                )
                evidence_records = list(result.scalars().all())
                
                summary = {
                    "total_evidence": len(evidence_records),
                    "by_type": {},
                    "by_status": {},
                    "total_size_mb": 0,
                    "collection_dates": []
                }
                
                for evidence in evidence_records:
                    # Count by type
                    evidence_type = evidence.type.value
                    summary["by_type"][evidence_type] = summary["by_type"].get(evidence_type, 0) + 1
                    
                    # Count by status
                    status = evidence.status.value
                    summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
                    
                    # Sum file sizes
                    if evidence.file_size:
                        summary["total_size_mb"] += evidence.file_size / (1024 * 1024)
                    
                    # Collect dates
                    if evidence.collected_at:
                        summary["collection_dates"].append(evidence.collected_at)
                
                return summary
                
        except Exception as e:
            logger.error("Failed to get evidence summary: %s", str(e))
            return {}

    async def _collection_worker(self, worker_name: str) -> None:
        """Background worker for evidence collection."""
        logger.info("Evidence collection worker %s started", worker_name)
        
        while self._is_running:
            try:
                # Get collection task
                try:
                    task = await asyncio.wait_for(
                        self._collection_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process collection
                await self._process_collection_task(task)
                
                self._collection_queue.task_done()
                
            except Exception as e:
                logger.error("Collection worker %s error: %s", worker_name, str(e))
                await asyncio.sleep(1)
        
        logger.info("Evidence collection worker %s stopped", worker_name)

    async def _determine_collection_types(self, alert: Alert) -> List[EvidenceCollectionType]:
        """Determine what types of evidence to collect."""
        collection_types = []
        
        # Always collect metadata
        collection_types.append(EvidenceCollectionType.METADATA_EXTRACTION)
        
        # Always collect screenshot for web-based violations
        if alert.platform in ["youtube", "instagram", "tiktok", "twitter", "facebook"]:
            collection_types.append(EvidenceCollectionType.SCREENSHOT)
        
        # Collect video for high-severity violations
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            collection_types.append(EvidenceCollectionType.VIDEO_CAPTURE)
        
        # Collect digital fingerprint for content violations
        if alert.type == AlertType.VIOLATION_DETECTED:
            collection_types.append(EvidenceCollectionType.DIGITAL_FINGERPRINT)
        
        return collection_types

    async def _collect_evidence_type(
        self,
        collection_type: EvidenceCollectionType,
        alert: Alert,
        evidence_path: str
    ) -> CollectionResult:
        """Collect specific type of evidence."""
        try:
            # Get violation URL from alert metadata
            violation_url = alert.metadata.get("violation_url") or alert.metadata.get("url")
            
            if not violation_url:
                return CollectionResult(
                    success=False,
                    error_message="No violation URL found in alert"
                )
            
            if collection_type == EvidenceCollectionType.SCREENSHOT:
                return await self.screenshot_collector.collect_screenshot(
                    violation_url, alert, evidence_path
                )
            
            elif collection_type == EvidenceCollectionType.VIDEO_CAPTURE:
                return await self.video_collector.collect_video(
                    violation_url, alert, evidence_path
                )
            
            elif collection_type == EvidenceCollectionType.METADATA_EXTRACTION:
                return await self.metadata_collector.collect_metadata(
                    violation_url, alert, evidence_path
                )
            
            elif collection_type == EvidenceCollectionType.DIGITAL_FINGERPRINT:
                return await self._collect_digital_fingerprint(
                    violation_url, alert, evidence_path
                )
            
            else:
                return CollectionResult(
                    success=False,
                    error_message=f"Unsupported collection type: {collection_type}"
                )
                
        except Exception as e:
            logger.error("Failed to collect evidence type %s: %s", collection_type, str(e))
            return CollectionResult(
                success=False,
                error_message=str(e)
            )

    async def _collect_digital_fingerprint(
        self,
        url: str,
        alert: Alert,
        evidence_path: str
    ) -> CollectionResult:
        """Collect digital fingerprint evidence."""
        try:
            # Create fingerprint data
            fingerprint_data = {
                "alert_id": alert.id,
                "url": url,
                "content_id": alert.content_id,
                "violation_type": alert.violation_type,
                "platform": alert.platform,
                "collected_at": datetime.utcnow().isoformat(),
                "fingerprint_hash": hashlib.sha256(
                    f"{alert.id}{url}{datetime.utcnow()}".encode()
                ).hexdigest()
            }
            
            # Save fingerprint
            fingerprint_path = f"{evidence_path}/fingerprint_{alert.id}_{int(datetime.utcnow().timestamp())}.json"
            
            async with aiofiles.open(fingerprint_path, 'w') as f:
                await f.write(json.dumps(fingerprint_data, indent=2))
            
            checksum = await self._calculate_checksum(fingerprint_path)
            file_size = os.path.getsize(fingerprint_path)
            
            return CollectionResult(
                success=True,
                file_path=fingerprint_path,
                file_size=file_size,
                checksum=checksum,
                metadata=fingerprint_data,
                collection_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Failed to collect digital fingerprint: %s", str(e))
            return CollectionResult(
                success=False,
                error_message=str(e)
            )

    async def _store_evidence_records(
        self,
        alert_id: str,
        collection_id: str,
        results: Dict[str, CollectionResult]
    ) -> None:
        """Store evidence records in database."""
        try:
            async with get_async_session() as session:
                for evidence_type, result in results.items():
                    evidence = Evidence(
                        id=str(uuid4()),
                        alert_id=alert_id,
                        collection_id=collection_id,
                        type=EvidenceType(evidence_type),
                        status=EvidenceStatus.COMPLETED if result.success else EvidenceStatus.FAILED,
                        file_path=result.file_path,
                        file_size=result.file_size,
                        checksum=result.checksum,
                        metadata=result.metadata,
                        error_message=result.error_message,
                        collected_at=result.collection_time or datetime.utcnow()
                    )
                    
                    session.add(evidence)
                
                await session.commit()
                
        except Exception as e:
            logger.error("Failed to store evidence records: %s", str(e))

    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

    async def _process_collection_task(self, task: Dict[str, Any]) -> None:
        """Process evidence collection task."""
        try:
            task_type = task.get("type")
            
            if task_type == "collect_evidence":
                alert = task["alert"]
                await self.collect_evidence(alert)
                
        except Exception as e:
            logger.error("Failed to process collection task: %s", str(e))

# Missing classes that are imported in __init__.py
class CollectionMethod:
    """Evidence collection method configuration"""
    def __init__(self, *args, **kwargs):
        pass

class EvidenceValidation:
    """Evidence validation configuration"""
    def __init__(self, *args, **kwargs):
        pass

class ScreenshotCapture:
    """Screenshot capture configuration"""
    def __init__(self, *args, **kwargs):
        pass

class MetadataExtractor:
    """Metadata extraction configuration"""
    def __init__(self, *args, **kwargs):
        pass
