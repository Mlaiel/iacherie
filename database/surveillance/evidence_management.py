"""Evidence Management Module
=========================

Comprehensive evidence collection and management system.
Handles automated screenshot capture, metadata extraction, and secure evidence storage.

Author: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All Rights Reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, BytesIO
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import hashlib
import base64
import os
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """
Evidence type enumeration."""

    SCREENSHOT = "screenshot"
    VIDEO_CAPTURE = "video_capture"
    METADATA = "metadata"
    WEBPAGE_ARCHIVE = "webpage_archive"
    NETWORK_TRACE = "network_trace"
    AUDIO_SAMPLE = "audio_sample"
    HASH_VERIFICATION = "hash_verification"


class EvidenceStatus(Enum):
    """Evidence status enumeration."""

    PENDING = "pending"
    COLLECTED = "collected"
    VERIFIED = "verified"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class EvidenceItem:
    """Evidence item data structure."""
    evidence_id: str
    violation_id: str
    evidence_type: EvidenceType
    status: EvidenceStatus
    file_path: Optional[str]
    file_size: Optional[int]
    checksum: Optional[str]
    metadata: Dict[str, Any]
    collected_at: datetime
    verified_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None


@dataclass
class ScreenshotRequest:
    """
Screenshot capture request."""
    url: str
    output_path: str
    viewport_width: int = 1920
    viewport_height: int = 1080
    wait_time: int = 3
    full_page: bool = True
    capture_options: Dict[str, Any] = None


class EvidenceCollector:
    """
    Main evidence collection coordinator.
    
    Manages evidence collection from multiple sources and formats.
    Ensures proper evidence chain of custody.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = Path(config.get("storage_path", "/tmp/evidence"))
        self.max_file_size = config.get("max_file_size", 100 * 1024 * 1024)  # 100MB
        self.retention_days = config.get("retention_days", 365)
        
        # Evidence collectors
        self.screenshot_collector: Optional[ScreenshotCapture] = None
        self.metadata_extractor: Optional[MetadataExtractor] = None
        self.evidence_storage: Optional[EvidenceStorage] = None
        
        # Collection queue
        self.collection_queue: asyncio.Queue = asyncio.Queue()
        self.collection_tasks: set = set()
        
    async def initialize(self) -> bool:
        """Initialize evidence collector."""
        try:
            # Create storage directory
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize sub-collectors
            await self._initialize_collectors()
            
            # Start collection worker
            await self._start_collection_worker()
            
            logger.info("EvidenceCollector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EvidenceCollector: {e}")
            return False
    
    async def _initialize_collectors(self) -> None:
        """Initialize evidence sub-collectors."""
        # Screenshot collector
        screenshot_config = self.config.get("screenshot", {})
        self.screenshot_collector = ScreenshotCapture(screenshot_config)
        await self.screenshot_collector.initialize()
        
        # Metadata extractor
        metadata_config = self.config.get("metadata", {})
        self.metadata_extractor = MetadataExtractor(metadata_config)
        await self.metadata_extractor.initialize()
        
        # Evidence storage
        storage_config = self.config.get("storage", {})
        storage_config["base_path"] = str(self.storage_path)
        self.evidence_storage = EvidenceStorage(storage_config)
        await self.evidence_storage.initialize()
        
        logger.info("Evidence sub-collectors initialized")
    
    async def _start_collection_worker(self) -> None:
        """Start evidence collection worker."""
        worker_task = asyncio.create_task(self._collection_worker())
        self.collection_tasks.add(worker_task)
        worker_task.add_done_callback(self.collection_tasks.discard)
        logger.info("Evidence collection worker started")
    
    async def _collection_worker(self) -> None:
        """Evidence collection worker loop."""
        while True:
            try:
                # Get collection request from queue
                collection_request = await self.collection_queue.get()
                
                # Process collection request
                await self._process_collection_request(collection_request)
                
                # Mark task as done
                self.collection_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in evidence collection worker: {e}")
                await asyncio.sleep(5)
    
    async def _process_collection_request(self, request: Dict[str, Any]) -> None:
        """Process evidence collection request."""
        try:
            evidence_type = EvidenceType(request["evidence_type"])
            violation_id = request["violation_id"]
            target_data = request["target_data"]
            
            # Generate evidence ID
            evidence_id = self._generate_evidence_id(violation_id, evidence_type)
            
            # Collect evidence based on type
            evidence_item = None
            
            if evidence_type == EvidenceType.SCREENSHOT:
                evidence_item = await self._collect_screenshot_evidence(
                    evidence_id, violation_id, target_data
                )
            elif evidence_type == EvidenceType.METADATA:
                evidence_item = await self._collect_metadata_evidence(
                    evidence_id, violation_id, target_data
                )
            elif evidence_type == EvidenceType.WEBPAGE_ARCHIVE:
                evidence_item = await self._collect_webpage_archive(
                    evidence_id, violation_id, target_data
                )
            elif evidence_type == EvidenceType.HASH_VERIFICATION:
                evidence_item = await self._collect_hash_verification(
                    evidence_id, violation_id, target_data
                )
            
            if evidence_item:
                # Store evidence item
                await self.evidence_storage.store_evidence(evidence_item)
                logger.info(f"Evidence collected: {evidence_id}")
            else:
                logger.error(f"Failed to collect evidence: {evidence_id}")
                
        except Exception as e:
            logger.error(f"Error processing collection request: {e}")
    
    def _generate_evidence_id(self, violation_id: str, evidence_type: EvidenceType) -> str:
        """Generate unique evidence ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        content = f"{violation_id}_{evidence_type.value}_{timestamp}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"evidence_{hash_suffix}_{timestamp}"
    
    async def _collect_screenshot_evidence(self, 
                                         evidence_id: str,
                                         violation_id: str,
                                         target_data: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Collect screenshot evidence."""
        try:
            url = target_data.get("detected_url")
            if not url:
                return None
            
            # Prepare screenshot request
            screenshot_path = self.storage_path / f"{evidence_id}_screenshot.png"
            
            screenshot_request = ScreenshotRequest(
                url=url,
                output_path=str(screenshot_path),
                viewport_width=1920,
                viewport_height=1080,
                wait_time=5,
                full_page=True
            )
            
            # Capture screenshot
            screenshot_result = await self.screenshot_collector.capture_screenshot(screenshot_request)
            
            if screenshot_result and screenshot_path.exists():
                file_size = screenshot_path.stat().st_size
                checksum = await self._calculate_file_checksum(screenshot_path)
                
                evidence_item = EvidenceItem(
                    evidence_id=evidence_id,
                    violation_id=violation_id,
                    evidence_type=EvidenceType.SCREENSHOT,
                    status=EvidenceStatus.COLLECTED,
                    file_path=str(screenshot_path),
                    file_size=file_size,
                    checksum=checksum,
                    metadata={
                        "url": url,
                        "viewport": f"{screenshot_request.viewport_width}x{screenshot_request.viewport_height}",
                        "capture_time": datetime.utcnow().isoformat(),
                        "screenshot_result": screenshot_result
                    },
                    collected_at=datetime.utcnow()
                )
                
                return evidence_item
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting screenshot evidence: {e}")
            return None
    
    async def _collect_metadata_evidence(self, 
                                       evidence_id: str,
                                       violation_id: str,
                                       target_data: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Collect metadata evidence."""
        try:
            url = target_data.get("detected_url")
            if not url:
                return None
            
            # Extract metadata
            metadata_result = await self.metadata_extractor.extract_metadata(url)
            
            if metadata_result:
                # Store metadata as JSON file
                metadata_path = self.storage_path / f"{evidence_id}_metadata.json"
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_result, f, indent=2, ensure_ascii=False, default=str)
                
                file_size = metadata_path.stat().st_size
                checksum = await self._calculate_file_checksum(metadata_path)
                
                evidence_item = EvidenceItem(
                    evidence_id=evidence_id,
                    violation_id=violation_id,
                    evidence_type=EvidenceType.METADATA,
                    status=EvidenceStatus.COLLECTED,
                    file_path=str(metadata_path),
                    file_size=file_size,
                    checksum=checksum,
                    metadata={
                        "url": url,
                        "extraction_time": datetime.utcnow().isoformat(),
                        "metadata_keys": list(metadata_result.keys()) if metadata_result else []
                    },
                    collected_at=datetime.utcnow()
                )
                
                return evidence_item
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting metadata evidence: {e}")
            return None
    
    async def _collect_webpage_archive(self, 
                                     evidence_id: str,
                                     violation_id: str,
                                     target_data: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Collect webpage archive evidence."""
        try:
            url = target_data.get("detected_url")
            if not url:
                return None
            
            # Archive webpage
            archive_path = self.storage_path / f"{evidence_id}_archive.html"
            
            # Download and save webpage content
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        with open(archive_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        file_size = archive_path.stat().st_size
                        checksum = await self._calculate_file_checksum(archive_path)
                        
                        evidence_item = EvidenceItem(
                            evidence_id=evidence_id,
                            violation_id=violation_id,
                            evidence_type=EvidenceType.WEBPAGE_ARCHIVE,
                            status=EvidenceStatus.COLLECTED,
                            file_path=str(archive_path),
                            file_size=file_size,
                            checksum=checksum,
                            metadata={
                                "url": url,
                                "status_code": response.status,
                                "content_type": response.headers.get("content-type", ""),
                                "archive_time": datetime.utcnow().isoformat()
                            },
                            collected_at=datetime.utcnow()
                        )
                        
                        return evidence_item
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting webpage archive: {e}")
            return None
    
    async def _collect_hash_verification(self, 
                                       evidence_id: str,
                                       violation_id: str,
                                       target_data: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Collect hash verification evidence."""
        try:
            # Generate hash verification data
            verification_data = {
                "original_fingerprint": target_data.get("fingerprint_hash"),
                "detected_url": target_data.get("detected_url"),
                "similarity_score": target_data.get("similarity_score"),
                "verification_time": datetime.utcnow().isoformat(),
                "platform": target_data.get("platform"),
                "verification_algorithm": "sha256"
            }
            
            # Create verification hash
            verification_content = json.dumps(verification_data, sort_keys=True)
            verification_hash = hashlib.sha256(verification_content.encode()).hexdigest()
            verification_data["verification_hash"] = verification_hash
            
            # Store verification data
            verification_path = self.storage_path / f"{evidence_id}_verification.json"
            
            with open(verification_path, 'w', encoding='utf-8') as f:
                json.dump(verification_data, f, indent=2, ensure_ascii=False)
            
            file_size = verification_path.stat().st_size
            checksum = await self._calculate_file_checksum(verification_path)
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                violation_id=violation_id,
                evidence_type=EvidenceType.HASH_VERIFICATION,
                status=EvidenceStatus.COLLECTED,
                file_path=str(verification_path),
                file_size=file_size,
                checksum=checksum,
                metadata=verification_data,
                collected_at=datetime.utcnow()
            )
            
            return evidence_item
            
        except Exception as e:
            logger.error(f"Error collecting hash verification: {e}")
            return None
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    async def collect_evidence(self, detection_result) -> List[str]:
        """Collect evidence for violation detection."""
        try:
            evidence_ids = []
            
            # Prepare collection requests
            collection_requests = [
                {
                    "evidence_type": "screenshot",
                    "violation_id": detection_result.target_id,
                    "target_data": {
                        "detected_url": detection_result.detected_url,
                        "platform": detection_result.platform,
                        "similarity_score": detection_result.similarity_score
                    }
                },
                {
                    "evidence_type": "metadata", 
                    "violation_id": detection_result.target_id,
                    "target_data": {
                        "detected_url": detection_result.detected_url,
                        "platform": detection_result.platform,
                        "evidence_data": detection_result.evidence_data
                    }
                },
                {
                    "evidence_type": "hash_verification",
                    "violation_id": detection_result.target_id,
                    "target_data": {
                        "fingerprint_hash": detection_result.target_id,
                        "detected_url": detection_result.detected_url,
                        "platform": detection_result.platform,
                        "similarity_score": detection_result.similarity_score
                    }
                }
            ]
            
            # Queue collection requests
            for request in collection_requests:
                await self.collection_queue.put(request)
                evidence_ids.append(
                    self._generate_evidence_id(
                        request["violation_id"], 
                        EvidenceType(request["evidence_type"])
                    )
                )
            
            logger.info(f"Queued {len(collection_requests)} evidence collection requests")
            return evidence_ids
            
        except Exception as e:
            logger.error(f"Error collecting evidence: {e}")
            return []
    
    async def get_evidence_status(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Get evidence collection status."""
        try:
            if self.evidence_storage:
                evidence_item = await self.evidence_storage.get_evidence(evidence_id)
                if evidence_item:
                    return {
                        "evidence_id": evidence_item.evidence_id,
                        "status": evidence_item.status.value,
                        "evidence_type": evidence_item.evidence_type.value,
                        "collected_at": evidence_item.collected_at.isoformat(),
                        "file_size": evidence_item.file_size,
                        "checksum": evidence_item.checksum
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting evidence status: {e}")
            return None
    
    async def cleanup_old_evidence(self) -> None:
        """Cleanup old evidence files based on retention policy."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            if self.evidence_storage:
                archived_count = await self.evidence_storage.archive_old_evidence(cutoff_date)
                logger.info(f"Archived {archived_count} old evidence items")
            
        except Exception as e:
            logger.error(f"Error cleaning up old evidence: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown evidence collector."""
        logger.info("Shutting down EvidenceCollector...")
        
        # Wait for pending collections
        await self.collection_queue.join()
        
        # Cancel collection tasks
        for task in self.collection_tasks:
            task.cancel()
        
        if self.collection_tasks:
            await asyncio.gather(*self.collection_tasks, return_exceptions=True)
        
        # Shutdown sub-collectors
        if self.screenshot_collector:
            await self.screenshot_collector.shutdown()
        if self.metadata_extractor:
            await self.metadata_extractor.shutdown()
        if self.evidence_storage:
            await self.evidence_storage.shutdown()
        
        logger.info("EvidenceCollector shutdown complete")


class ScreenshotCapture:
    """
    Screenshot capture system using headless browser.
    
    Captures high-quality screenshots with evidence metadata.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser_type = config.get("browser_type", "chromium")
        self.headless = config.get("headless", True)
        self.timeout = config.get("timeout", 30)
        self.browser = None
        self.browser_context = None
        
    async def initialize(self) -> bool:
        """Initialize screenshot capture system."""
        try:
            # Initialize Playwright browser
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            
            # Create browser context
            self.browser_context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            logger.info("ScreenshotCapture initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ScreenshotCapture: {e}")
            return False
    
    async def capture_screenshot(self, request: ScreenshotRequest) -> Optional[Dict[str, Any]]:
        """Capture screenshot based on request."""
        try:
            if not self.browser_context:
                logger.error("Browser context not initialized")
                return None
            
            # Create new page
            page = await self.browser_context.new_page()
            
            # Set viewport
            await page.set_viewport_size({
                "width": request.viewport_width,
                "height": request.viewport_height
            })
            
            # Navigate to URL
            start_time = datetime.utcnow()
            
            try:
                response = await page.goto(request.url, timeout=self.timeout * 1000)
                
                if not response or response.status >= 400:
                    logger.warning(f"Failed to load page: {request.url} (status: {response.status if response else 'timeout'})")
                    await page.close()
                    return None
                
                # Wait for page to load
                await page.wait_for_timeout(request.wait_time * 1000)
                
                # Additional wait for dynamic content
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    pass  # Continue even if networkidle timeout
                
                # Capture screenshot
                screenshot_options = {
                    "path": request.output_path,
                    "full_page": request.full_page,
                    "type": "png"
                }
                
                if request.capture_options:
                    screenshot_options.update(request.capture_options)
                
                await page.screenshot(**screenshot_options)
                
                end_time = datetime.utcnow()
                
                # Get page metadata
                page_title = await page.title()
                page_url = page.url
                
                result = {
                    "success": True,
                    "url": request.url,
                    "final_url": page_url,
                    "title": page_title,
                    "viewport": f"{request.viewport_width}x{request.viewport_height}",
                    "screenshot_path": request.output_path,
                    "capture_duration": (end_time - start_time).total_seconds(),
                    "response_status": response.status,
                    "captured_at": end_time.isoformat()
                }
                
                await page.close()
                return result
                
            except Exception as e:
                await page.close()
                logger.error(f"Error capturing screenshot for {request.url}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in screenshot capture: {e}")
            return None
    
    async def capture_multiple_screenshots(self, requests: List[ScreenshotRequest]) -> List[Dict[str, Any]]:
        """Capture multiple screenshots concurrently."""
        try:
            # Limit concurrent captures to avoid resource exhaustion
            semaphore = asyncio.Semaphore(5)
            
            async def capture_with_semaphore(request):
                async with semaphore:
                    return await self.capture_screenshot(request)
            
            # Execute captures concurrently
            tasks = [capture_with_semaphore(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [
                result for result in results 
                if isinstance(result, dict) and result.get("success")
            ]
            
            logger.info(f"Captured {len(successful_results)}/{len(requests)} screenshots successfully")
            return successful_results
            
        except Exception as e:
            logger.error(f"Error capturing multiple screenshots: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Shutdown screenshot capture system."""
        try:
            if self.browser_context:
                await self.browser_context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("ScreenshotCapture shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down ScreenshotCapture: {e}")


class MetadataExtractor:
    """
    Metadata extraction system.
    
    Extracts comprehensive metadata from web content and media files.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.extraction_timeout = config.get("extraction_timeout", 30)
        self.user_agent = config.get("user_agent", "IA-Influencer-Evidence-Bot/1.0")
        
    async def initialize(self) -> bool:
        """Initialize metadata extractor."""
        try:
            logger.info("MetadataExtractor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MetadataExtractor: {e}")
            return False
    
    async def extract_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from URL."""
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=self.extraction_timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_type = response.headers.get("content-type", "")
                        
                        # Parse HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        metadata = {
                            "url": url,
                            "status_code": response.status,
                            "content_type": content_type,
                            "extraction_time": datetime.utcnow().isoformat(),
                            "page_title": self._extract_title(soup),
                            "meta_description": self._extract_meta_description(soup),
                            "meta_keywords": self._extract_meta_keywords(soup),
                            "open_graph": self._extract_open_graph(soup),
                            "twitter_cards": self._extract_twitter_cards(soup),
                            "canonical_url": self._extract_canonical_url(soup),
                            "structured_data": self._extract_structured_data(soup),
                            "images": self._extract_images(soup, url),
                            "videos": self._extract_videos(soup, url),
                            "links": self._extract_links(soup, url),
                            "text_content": self._extract_text_content(soup),
                            "page_stats": {
                                "content_length": len(content),
                                "word_count": len(soup.get_text().split()),
                                "image_count": len(soup.find_all('img')),
                                "link_count": len(soup.find_all('a'))
                            }
                        }
                        
                        return metadata
                    
                    else:
                        logger.warning(f"Failed to fetch URL {url}: status {response.status}")
                        return None
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords."""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph metadata."""
        og_data = {}
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                og_data[property_name] = content
        
        return og_data
    
    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
Extract Twitter Card metadata."""
        twitter_data = {}
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                twitter_data[name] = content
        
        return twitter_data
    
    def _extract_canonical_url(self, soup: BeautifulSoup) -> str:
        """
Extract canonical URL."""
        canonical = soup.find('link', rel='canonical')
        return canonical.get('href', '') if canonical else ""
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD)."""
        structured_data = []
        
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return structured_data
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
Extract image information."""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags[:20]:  # Limit to first 20 images
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src:
                # Convert relative URLs to absolute
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(base_url, src)
                
                images.append({
                    'src': src,
                    'alt': alt,
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        return images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
Extract video information."""
        videos = []
        
        # Video tags
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src', '')
            if not src:
                source = video.find('source')
                src = source.get('src', '') if source else ''
            
            if src:
                videos.append({
                    'src': src,
                    'type': 'video',
                    'controls': video.has_attr('controls'),
                    'autoplay': video.has_attr('autoplay')
                })
        
        # YouTube embeds
        youtube_iframes = soup.find_all('iframe', src=lambda x: x and 'youtube.com' in x)
        for iframe in youtube_iframes:
            videos.append({
                'src': iframe.get('src', ''),
                'type': 'youtube_embed',
                'width': iframe.get('width', ''),
                'height': iframe.get('height', '')
            })
        
        return videos
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
Extract link information."""
        links = []
        link_tags = soup.find_all('a', href=True)
        
        for link in link_tags[:50]:  # Limit to first 50 links
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if href and not href.startswith('#'):
                # Convert relative URLs to absolute
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(base_url, href)
                
                links.append({
                    'href': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'rel': link.get('rel', [])
                })
        
        return links
    
    def _extract_text_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
Extract text content from main elements."""
        content = {}
        
        # Main content areas
        main_selectors = ['main', 'article', '.content', '#content', '.main']
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                content['main_content'] = element.get_text().strip()[:2000]  # Limit to 2000 chars
                break
        
        # Headings
        headings = []
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            for h in h_tags:
                headings.append({
                    'level': i,
                    'text': h.get_text().strip()
                })
        
        content['headings'] = headings[:10]  # Limit to first 10 headings
        
        # Full text (cleaned)
        full_text = soup.get_text()
        # Clean up whitespace
        full_text = ' '.join(full_text.split())
        content['full_text'] = full_text[:5000]  # Limit to 5000 chars
        
        return content
    
    async def shutdown(self) -> None:
        """
Shutdown metadata extractor."""
        logger.info("MetadataExtractor shutdown complete")


class EvidenceStorage:
    """
    Evidence storage and management system.
    
    Handles secure storage, retrieval, and archival of evidence files.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = Path(config.get("base_path", "/tmp/evidence"))
        self.database_url = config.get("database_url")
        self.encryption_enabled = config.get("encryption_enabled", True)
        self.evidence_registry: Dict[str, EvidenceItem] = {}
        
    async def initialize(self) -> bool:
        """Initialize evidence storage."""
        try:
            # Create storage directories
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            (self.base_path / "screenshots").mkdir(exist_ok=True)
            (self.base_path / "metadata").mkdir(exist_ok=True)
            (self.base_path / "archives").mkdir(exist_ok=True)
            (self.base_path / "verification").mkdir(exist_ok=True)
            
            # Initialize database connection if configured
            if self.database_url:
                await self._initialize_database()
            
            logger.info("EvidenceStorage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EvidenceStorage: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize database for evidence registry."""
        # Database initialization would go here
        pass
    
    async def store_evidence(self, evidence_item: EvidenceItem) -> bool:
        """
Store evidence item."""
        try:
            # Store in registry
            self.evidence_registry[evidence_item.evidence_id] = evidence_item
            
            # Store in database if configured
            if self.database_url:
                await self._store_evidence_in_database(evidence_item)
            
            logger.info(f"Evidence stored: {evidence_item.evidence_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing evidence {evidence_item.evidence_id}: {e}")
            return False
    
    async def _store_evidence_in_database(self, evidence_item: EvidenceItem) -> None:
        """Store evidence metadata in database."""
        # Database storage implementation would go here
        pass
    
    async def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        """
Get evidence item by ID."""
        try:
            # Try registry first
            if evidence_id in self.evidence_registry:
                return self.evidence_registry[evidence_id]
            
            # Try database if configured
            if self.database_url:
                return await self._get_evidence_from_database(evidence_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting evidence {evidence_id}: {e}")
            return None
    
    async def _get_evidence_from_database(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Get evidence from database."""
        # Database retrieval implementation would go here
        return None
    
    async def archive_old_evidence(self, cutoff_date: datetime) -> int:
        """
Archive old evidence items."""
        try:
            archived_count = 0
            
            for evidence_id, evidence_item in list(self.evidence_registry.items()):
                if evidence_item.collected_at < cutoff_date:
                    # Archive the evidence
                    await self._archive_evidence_item(evidence_item)
                    archived_count += 1
            
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving old evidence: {e}")
            return 0
    
    async def _archive_evidence_item(self, evidence_item: EvidenceItem) -> None:
        """Archive individual evidence item."""
        try:
            # Move file to archive directory
            if evidence_item.file_path:
                current_path = Path(evidence_item.file_path)
                if current_path.exists():
                    archive_dir = self.base_path / "archives" / evidence_item.collected_at.strftime("%Y/%m")
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    archive_path = archive_dir / current_path.name
                    current_path.rename(archive_path)
                    
                    # Update evidence item
                    evidence_item.file_path = str(archive_path)
                    evidence_item.status = EvidenceStatus.ARCHIVED
                    evidence_item.archived_at = datetime.utcnow()
            
            logger.info(f"Evidence archived: {evidence_item.evidence_id}")
            
        except Exception as e:
            logger.error(f"Error archiving evidence {evidence_item.evidence_id}: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown evidence storage."""
        logger.info("EvidenceStorage shutdown complete")


# Global evidence collector instance
_evidence_collector: Optional[EvidenceCollector] = None


def get_evidence_collector() -> Optional[EvidenceCollector]:
    """Get global evidence collector instance."""
    return _evidence_collector


def initialize_evidence_collector(config: Dict[str, Any]) -> EvidenceCollector:
    """
Initialize global evidence collector."""
    global _evidence_collector
    _evidence_collector = EvidenceCollector(config)
    return _evidence_collector
