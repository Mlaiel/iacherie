"""Brand Agent - Advanced Brand Management & Identity Protection System

Industrial-grade brand protection, identity management, and reputation monitoring for content creators.
Handles brand consistency, trademark protection, anti-counterfeiting, and brand value optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from pathlib import Path

import cv2
import torch
import transformers
from PIL import Image, ImageFont, ImageDraw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import requests
from bs4 import BeautifulSoup
import webcolors

from ..base import BaseAgent, AgentRequest, AgentResponse, AgentStatus, AgentPriority
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.ml_utils import VectorDatabase, ImageProcessor, TextAnalyzer
from ...content_protection.fingerprinting import VisualFingerprinter

logger = logging.getLogger(__name__)

class BrandThreatLevel(Enum):
    """
Brand threat severity levels"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BrandAssetType(Enum):
    """Types of brand assets to protect"""

    LOGO = "logo"
    TRADEMARK = "trademark"
    SLOGAN = "slogan"
    COLOR_PALETTE = "color_palette"
    TYPOGRAPHY = "typography"
    AUDIO_SIGNATURE = "audio_signature"
    VISUAL_STYLE = "visual_style"
    BRAND_NAME = "brand_name"
    DOMAIN_NAME = "domain_name"

class BrandViolationType(Enum):
    """Types of brand violations detected"""

    LOGO_MISUSE = "logo_misuse"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    COUNTERFEITING = "counterfeiting"
    UNAUTHORIZED_USE = "unauthorized_use"
    BRAND_IMPERSONATION = "brand_impersonation"
    COLOR_THEFT = "color_theft"
    STYLE_COPYING = "style_copying"
    DOMAIN_SQUATTING = "domain_squatting"

@dataclass
class BrandAsset:
    """Brand asset definition and metadata"""
    asset_id: str
    asset_type: BrandAssetType
    name: str
    description: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "premium"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    fingerprint: Optional[str] = None
    visual_features: Optional[Dict[str, Any]] = None
    ai_generated_variations: List[str] = field(default_factory=list)
    blockchain_hash: Optional[str] = None
    legal_registrations: Dict[str, str] = field(default_factory=dict)
    usage_rights: Dict[str, Any] = field(default_factory=dict)
    monetization_value: float = 0.0

@dataclass
class BrandViolation:
    """Detected brand violation with evidence"""
    violation_id: str
    asset_id: str
    violation_type: BrandViolationType
    threat_level: BrandThreatLevel
    source_url: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    evidence: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    potential_damage: float = 0.0
    legal_actions_available: List[str] = field(default_factory=list)
    auto_takedown_eligible: bool = False

@dataclass
class BrandMetrics:
    """
Comprehensive brand performance metrics"""
    brand_id: str
    recognition_score: float = 0.0
    sentiment_score: float = 0.0
    engagement_rate: float = 0.0
    protection_coverage: float = 0.0
    violation_count: int = 0
    market_value: float = 0.0
    growth_rate: float = 0.0
    competitive_position: int = 0
    trust_index: float = 0.0
    innovation_score: float = 0.0
    color_palette: Optional[List[str]] = None
    font_family: Optional[str] = None

@dataclass
class BrandViolation:
    """
Brand violation detection result"""
    violation_id: str
    asset_id: str
    violation_type: BrandViolationType
    threat_level: BrandThreatLevel
    confidence_score: float
    detected_at: datetime
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    screenshot_path: Optional[str] = None
    legal_risk_score: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class BrandConsistencyReport:
    """
Brand consistency analysis report"""
    report_id: str
    brand_id: str
    analyzed_assets: List[str]
    consistency_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    color_consistency: float
    typography_consistency: float
    style_consistency: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

class BrandAgent(BaseAgent):
    """
    Advanced Brand Management & Identity Protection System
    
    Provides comprehensive brand protection including:
    - Visual brand identity protection
    - Trademark and copyright monitoring
    - Anti-counterfeiting detection
    - Brand consistency analysis
    - Reputation monitoring
    - Automated takedown requests
    """
    def __init__(self, agent_id: str = "brand_agent"):
        super().__init__(agent_id)
        self.name = "Brand Protection Agent"
        self.description = "Advanced brand management and identity protection system"
        self.version = "2.1.0"
        
        # Initialize ML models and processors
        self._initialize_models()
        
        # Brand assets storage
        self.brand_assets: Dict[str, BrandAsset] = {}
        self.violation_history: List[BrandViolation] = []
        
        # Performance monitors
        self.detection_monitor = PerformanceMonitor("brand_detection")
        self.consistency_monitor = PerformanceMonitor("brand_consistency")
        
        # Content encryption for sensitive brand data
        self.encryption = ContentEncryption()
        
        logger.info(f"Brand Agent {self.agent_id} initialized successfully")

    def _initialize_models(self) -> None:
        """Initialize ML models for brand analysis"""
        try:
            # Visual similarity model for logo/image comparison
            self.visual_processor = ImageProcessor()
            self.visual_fingerprinter = VisualFingerprinter()
            
            # Text analysis model for trademark/slogan protection
            self.text_analyzer = TextAnalyzer()
            self.nlp = spacy.load("en_core_web_lg")
            
            # Color analysis tools
            self.color_extractor = self._initialize_color_extractor()
            
            # Typography analyzer
            self.font_detector = self._initialize_font_detector()
            
            # Vector database for similarity search
            self.vector_db = VectorDatabase("brand_vectors")
            
            logger.info("Brand analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize brand models: {str(e)}")
            raise

    def _initialize_color_extractor(self):
        """Initialize advanced color extraction and analysis"""
        from sklearn.cluster import KMeans
        
        class ColorExtractor:
            def __init__(self):
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
            def extract_dominant_colors(self, image_path: str) -> List[str]:
                """
Extract dominant colors from image"""
                try:
                    image = cv2.imread(image_path)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR_RGB)
                    image = image.reshape((image.shape[0] * image.shape[1], 3))
                    
                    self.kmeans.fit(image)
                    colors = self.kmeans.cluster_centers_
                    
                    # Convert to hex colors
                    hex_colors = []
                    for color in colors:
                        hex_color = "#{:02x}{:02x}{:02x}".format(
                            int(color[0]), int(color[1]), int(color[2])
                        )
                        hex_colors.append(hex_color)
                    
                    return hex_colors
                except Exception as e:
                    logger.error(f"Color extraction failed: {str(e)}")
                    return []
                    
            def calculate_color_similarity(self, palette1: List[str], palette2: List[str]) -> float:
                """Calculate similarity between color palettes"""
                try:
                    similarities = []
                    for color1 in palette1:
                        best_match = 0.0
                        rgb1 = self._hex_to_rgb(color1)
                        
                        for color2 in palette2:
                            rgb2 = self._hex_to_rgb(color2)
                            similarity = self._color_distance(rgb1, rgb2)
                            best_match = max(best_match, similarity)
                        
                        similarities.append(best_match)
                    
                    return sum(similarities) / len(similarities) if similarities else 0.0
                except Exception:
                    return 0.0
                    
            def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
                """
Convert hex color to RGB"""
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                
            def _color_distance(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
                """
Calculate color distance (inverse similarity)"""
                distance = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
                max_distance = (3 * 255 ** 2) ** 0.5
                return 1.0 - (distance / max_distance)
        
        return ColorExtractor()

    def _initialize_font_detector(self):
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
                max_distance = (3 * 255 ** 2) ** 0.5
                return 1.0 - (distance / max_distance)
        
        return ColorExtractor()

    def _initialize_font_detector(self):
        """
Initialize font detection and analysis"""
        class FontDetector:
            def __init__(self):
                # Common font families for detection
                self.common_fonts = [
                    'Arial', 'Helvetica', 'Times New Roman', 'Georgia',
                    'Verdana', 'Tahoma', 'Trebuchet MS', 'Impact',
                    'Comic Sans MS', 'Courier New', 'Lucida Console'
                ]
                
            def detect_font_family(self, text_image_path: str) -> Optional[str]:
                """
Detect font family from text image"""
                try:
                    # This would use OCR and font recognition
                    # For now, return detected font or None
                    return "Arial"  # Placeholder - real implementation would use font detection
                except Exception:
                    return None
                    
            def analyze_typography_consistency(self, images: List[str]) -> Dict[str, Any]:
                """Analyze typography consistency across multiple images"""
                fonts_detected = []
                for image_path in images:
                    font = self.detect_font_family(image_path)
                    if font:
                        fonts_detected.append(font)
                
                if not fonts_detected:
                    return {"consistency_score": 0.0, "fonts_found": []}
                
                # Calculate consistency based on font usage
                font_counts = {}
                for font in fonts_detected:
                    font_counts[font] = font_counts.get(font, 0) + 1
                
                most_common_font = max(font_counts, key=font_counts.get)
                consistency_score = font_counts[most_common_font] / len(fonts_detected)
                
                return {
                    "consistency_score": consistency_score,
                    "fonts_found": list(font_counts.keys()),
                    "primary_font": most_common_font,
                    "font_distribution": font_counts
                }
        
        return FontDetector()

    async def process_request(self, request: AgentRequest) -> Dict[str, Any]:
        """Process brand protection requests"""
        try:
            self._update_status(AgentStatus.BUSY)
            
            action = request.action
            data = request.data
            
            logger.info(f"Processing brand request: {action}")
            
            if action == "register_brand_asset":
                result = await self._register_brand_asset(data)
            elif action == "detect_violations":
                result = await self._detect_brand_violations(data)
            elif action == "analyze_consistency":
                result = await self._analyze_brand_consistency(data)
            elif action == "monitor_brand":
                result = await self._monitor_brand_mentions(data)
            elif action == "generate_protection_report":
                result = await self._generate_protection_report(data)
            elif action == "submit_takedown_request":
                result = await self._submit_takedown_request(data)
            elif action == "calculate_brand_value":
                result = await self._calculate_brand_value(data)
            elif action == "optimize_brand_presence":
                result = await self._optimize_brand_presence(data)
            else:
                raise ValueError(f"Unknown action: {action}")
                
            self._update_status(AgentStatus.ACTIVE)
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Brand request processing failed: {str(e)}")
            self._update_status(AgentStatus.ERROR)
            return {"success": False, "error": str(e)}

    async def _register_brand_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register and fingerprint a new brand asset"""
        try:
            asset_type = BrandAssetType(data.get("asset_type"))
            asset_name = data.get("name")
            file_path = data.get("file_path")
            description = data.get("description", "")
            
            asset_id = f"asset_{hashlib.md5(f'{asset_name}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}"
            
            # Create brand asset
            brand_asset = BrandAsset(
                asset_id=asset_id,
                asset_type=asset_type,
                name=asset_name,
                description=description,
                file_path=file_path,
                protection_level=data.get("protection_level", "standard")
            )
            
            # Generate fingerprint based on asset type
            if asset_type == BrandAssetType.LOGO and file_path:
                brand_asset.fingerprint = await self._generate_visual_fingerprint(file_path)
                brand_asset.visual_features = await self._extract_visual_features(file_path)
                brand_asset.color_palette = self.color_extractor.extract_dominant_colors(file_path)
                
            elif asset_type == BrandAssetType.TRADEMARK:
                brand_asset.fingerprint = await self._generate_text_fingerprint(asset_name)
                
            elif asset_type == BrandAssetType.SLOGAN:
                brand_asset.fingerprint = await self._generate_text_fingerprint(data.get("slogan_text", ""))
                
            elif asset_type == BrandAssetType.COLOR_PALETTE:
                brand_asset.color_palette = data.get("colors", [])
                brand_asset.fingerprint = hashlib.md5(''.join(brand_asset.color_palette).encode()).hexdigest()
                
            # Store asset
            self.brand_assets[asset_id] = brand_asset
            
            # Save to vector database for similarity search
            if brand_asset.fingerprint:
                await self._store_asset_vector(brand_asset)
            
            logger.info(f"Brand asset registered: {asset_id} ({asset_type.value})")
            
            return {
                "asset_id": asset_id,
                "fingerprint": brand_asset.fingerprint,
                "features_extracted": bool(brand_asset.visual_features),
                "colors_detected": len(brand_asset.color_palette) if brand_asset.color_palette else 0
            }
            
        except Exception as e:
            logger.error(f"Brand asset registration failed: {str(e)}")
            raise

    async def _generate_visual_fingerprint(self, image_path: str) -> str:
        """Generate perceptual hash for visual content"""
        try:
            return await self.visual_fingerprinter.generate_fingerprint(image_path)
        except Exception as e:
            logger.error(f"Visual fingerprint generation failed: {str(e)}")
            return ""

    async def _generate_text_fingerprint(self, text: str) -> str:
        """Generate semantic fingerprint for text content"""
        try:
            # Create semantic embedding using the text analyzer
            embedding = await self.text_analyzer.get_embedding(text)
            # Convert embedding to hash for fingerprint
            fingerprint = hashlib.md5(str(embedding).encode()).hexdigest()
            return fingerprint
        except Exception as e:
            logger.error(f"Text fingerprint generation failed: {str(e)}")
            return hashlib.md5(text.encode()).hexdigest()

    async def _extract_visual_features(self, image_path: str) -> Dict[str, Any]:
        """Extract comprehensive visual features from image"""
        try:
            features = {}
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return features
                
            # Basic image properties
            height, width, channels = image.shape
            features["dimensions"] = {"width": width, "height": height, "channels": channels}
            features["aspect_ratio"] = width / height
            
            # Color analysis
            features["dominant_colors"] = self.color_extractor.extract_dominant_colors(image_path)
            
            # Edge detection for shape analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            features["edge_density"] = float(edge_density)
            
            # Texture analysis using Local Binary Pattern
            from skimage.feature import local_binary_pattern
            lbp = local_binary_pattern(gray, 24, 8, method='uniform')
            hist, _ = np.histogram(lbp.ravel(), bins=26, range=(0, 26))
            features["texture_histogram"] = hist.tolist()
            
            # Contour analysis for shape complexity
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features["contour_count"] = len(contours)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                features["main_contour_area"] = float(cv2.contourArea(largest_contour))
                features["main_contour_perimeter"] = float(cv2.arcLength(largest_contour, True))
            
            return features
            
        except Exception as e:
            logger.error(f"Visual feature extraction failed: {str(e)}")
            return {}

    async def _store_asset_vector(self, asset: BrandAsset) -> None:
        """Store asset vector in database for similarity search"""
        try:
            if asset.fingerprint:
                # Convert fingerprint to vector for storage
                vector_data = {
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type.value,
                    "fingerprint": asset.fingerprint,
                    "features": asset.visual_features,
                    "metadata": asset.metadata
                }
                
                await self.vector_db.store_vector(
                    vector_id=asset.asset_id,
                    vector_data=vector_data
                )
                
        except Exception as e:
            logger.error(f"Asset vector storage failed: {str(e)}")

    async def _detect_brand_violations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect brand violations across multiple sources"""
        try:
            search_params = data.get("search_params", {})
            brand_id = data.get("brand_id")
            monitoring_scope = data.get("scope", ["web", "social_media", "marketplaces"])
            
            violations_detected = []
            
            for scope in monitoring_scope:
                if scope == "web":
                    web_violations = await self._scan_web_violations(search_params)
                    violations_detected.extend(web_violations)
                    
                elif scope == "social_media":
                    social_violations = await self._scan_social_media_violations(search_params)
                    violations_detected.extend(social_violations)
                    
                elif scope == "marketplaces":
                    marketplace_violations = await self._scan_marketplace_violations(search_params)
                    violations_detected.extend(marketplace_violations)
            
            # Analyze and prioritize violations
            prioritized_violations = await self._prioritize_violations(violations_detected)
            
            # Generate automated recommendations
            recommendations = await self._generate_violation_recommendations(prioritized_violations)
            
            logger.info(f"Brand violation scan completed: {len(violations_detected)} violations found")
            
            return {
                "violations_found": len(violations_detected),
                "high_priority_violations": len([v for v in prioritized_violations if v.threat_level in [BrandThreatLevel.HIGH, BrandThreatLevel.CRITICAL]]),
                "violations": [self._violation_to_dict(v) for v in prioritized_violations],
                "recommendations": recommendations,
                "scan_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Brand violation detection failed: {str(e)}")
            raise

    async def _scan_web_violations(self, search_params: Dict[str, Any]) -> List[BrandViolation]:
        """Scan web for brand violations"""
        violations = []
        
        try:
            # Search engines and web crawling
            search_queries = search_params.get("search_queries", [])
            
            for query in search_queries:
                # Perform web search (using Google Custom Search API or similar)
                search_results = await self._perform_web_search(query)
                
                for result in search_results:
                    violation = await self._analyze_web_result_for_violation(result, search_params)
                    if violation:
                        violations.append(violation)
                        
        except Exception as e:
            logger.error(f"Web violation scanning failed: {str(e)}")
            
        return violations

    async def _scan_social_media_violations(self, search_params: Dict[str, Any]) -> List[BrandViolation]:
        """Scan social media platforms for brand violations"""
        violations = []
        
        try:
            platforms = search_params.get("platforms", ["instagram", "facebook", "twitter", "tiktok"])
            brand_keywords = search_params.get("brand_keywords", [])
            
            for platform in platforms:
                for keyword in brand_keywords:
                    platform_violations = await self._scan_platform_violations(platform, keyword, search_params)
                    violations.extend(platform_violations)
                    
        except Exception as e:
            logger.error(f"Social media violation scanning failed: {str(e)}")
            
        return violations

    async def _scan_marketplace_violations(self, search_params: Dict[str, Any]) -> List[BrandViolation]:
        """Scan online marketplaces for counterfeit products"""
        violations = []
        
        try:
            marketplaces = search_params.get("marketplaces", ["amazon", "ebay", "alibaba", "etsy"])
            product_keywords = search_params.get("product_keywords", [])
            
            for marketplace in marketplaces:
                for keyword in product_keywords:
                    marketplace_violations = await self._scan_marketplace_listings(marketplace, keyword, search_params)
                    violations.extend(marketplace_violations)
                    
        except Exception as e:
            logger.error(f"Marketplace violation scanning failed: {str(e)}")
            
        return violations

    async def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search using search engines"""
        # This would integrate with Google Custom Search API, Bing API, etc.
        # For now, return placeholder results
        return [
            {
                "url": f"https://example.com/search-result-{i}",
                "title": f"Search result {i} for {query}",
                "description": f"Description for search result {i}",
                "image_urls": []
            }
            for i in range(5)
        ]

    async def _analyze_web_result_for_violation(self, result: Dict[str, Any], search_params: Dict[str, Any]) -> Optional[BrandViolation]:
        """Analyze a web search result for potential brand violations"""
        try:
            url = result.get("url")
            title = result.get("title", "")
            description = result.get("description", "")
            
            # Check for trademark violations in text
            text_violation_score = await self._calculate_text_violation_score(title + " " + description, search_params)
            
            # Check for visual violations if images present
            visual_violation_score = 0.0
            image_urls = result.get("image_urls", [])
            if image_urls:
                visual_violation_score = await self._calculate_visual_violation_score(image_urls, search_params)
            
            # Determine overall violation score
            overall_score = max(text_violation_score, visual_violation_score)
            
            if overall_score > 0.7:  # High confidence threshold
                violation_id = f"web_{hashlib.md5(url.encode()).hexdigest()[:12]}"
                
                return BrandViolation(
                    violation_id=violation_id,
                    asset_id=search_params.get("primary_asset_id", ""),
                    violation_type=BrandViolationType.UNAUTHORIZED_USE,
                    threat_level=self._score_to_threat_level(overall_score),
                    confidence_score=overall_score,
                    detected_at=datetime.utcnow(),
                    source_url=url,
                    source_platform="web",
                    evidence={
                        "title": title,
                        "description": description,
                        "text_score": text_violation_score,
                        "visual_score": visual_violation_score
                    },
                    similarity_score=overall_score,
                    legal_risk_score=self._calculate_legal_risk(overall_score, "web"),
                    recommended_actions=self._generate_recommended_actions(overall_score, "web")
                )
                
        except Exception as e:
            logger.error(f"Web result analysis failed: {str(e)}")
            
        return None

    async def _calculate_text_violation_score(self, text: str, search_params: Dict[str, Any]) -> float:
        """Calculate text-based violation score"""
        try:
            protected_terms = search_params.get("protected_terms", [])
            brand_name = search_params.get("brand_name", "")
            
            violation_score = 0.0
            
            # Check for exact matches
            text_lower = text.lower()
            for term in protected_terms:
                if term.lower() in text_lower:
                    violation_score = max(violation_score, 0.9)
            
            # Check brand name variations
            if brand_name:
                brand_variations = self._generate_brand_variations(brand_name)
                for variation in brand_variations:
                    if variation.lower() in text_lower:
                        violation_score = max(violation_score, 0.8)
            
            # Semantic similarity check
            if brand_name and len(text) > 10:
                semantic_similarity = await self._calculate_semantic_similarity(text, brand_name)
                violation_score = max(violation_score, semantic_similarity * 0.7)
                
            return violation_score
            
        except Exception as e:
            logger.error(f"Text violation score calculation failed: {str(e)}")
            return 0.0

    def _generate_brand_variations(self, brand_name: str) -> List[str]:
        """Generate common variations of brand name for detection"""
        variations = [brand_name]
        
        # Remove spaces
        variations.append(brand_name.replace(" ", ""))
        
        # Add common misspellings (simplified)
        for i, char in enumerate(brand_name):
            if char.isalpha():
                # Character substitution
                for replacement in "aeiou":
                    if replacement != char.lower():
                        variation = brand_name[:i] + replacement + brand_name[i+1:]
                        variations.append(variation)
        
        # Add with common suffixes
        suffixes = ["co", "inc", "llc", "ltd", "corp"]
        for suffix in suffixes:
            variations.append(f"{brand_name} {suffix}")
            variations.append(f"{brand_name}{suffix}")
        
        return list(set(variations))

    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts"""
        try:
            # Use the text analyzer for semantic similarity
            similarity = await self.text_analyzer.calculate_similarity(text1, text2)
            return similarity
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return 0.0

    async def _calculate_visual_violation_score(self, image_urls: List[str], search_params: Dict[str, Any]) -> float:
        """Calculate visual-based violation score"""
        max_score = 0.0
        
        try:
            protected_asset_ids = search_params.get("protected_asset_ids", [])
            
            for image_url in image_urls[:5]:  # Limit to first 5 images
                # Download and analyze image
                image_path = await self._download_image(image_url)
                if not image_path:
                    continue
                    
                # Generate fingerprint for comparison
                image_fingerprint = await self._generate_visual_fingerprint(image_path)
                
                # Compare with protected assets
                for asset_id in protected_asset_ids:
                    if asset_id in self.brand_assets:
                        asset = self.brand_assets[asset_id]
                        if asset.fingerprint:
                            similarity = await self._calculate_fingerprint_similarity(
                                image_fingerprint, asset.fingerprint
                            )
                            max_score = max(max_score, similarity)
                
                # Clean up downloaded file
                Path(image_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Visual violation score calculation failed: {str(e)}")
            
        return max_score

    async def _download_image(self, image_url: str) -> Optional[str]:
        """Download image for analysis"""
        try:
            import tempfile
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file.write(content)
                            return temp_file.name
                            
        except Exception as e:
            logger.error(f"Image download failed: {str(e)}")
            
        return None

    async def _calculate_fingerprint_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between two fingerprints"""
        try:
            # For hash-based fingerprints, use Hamming distance
            if len(fingerprint1) == len(fingerprint2):
                differences = sum(c1 != c2 for c1, c2 in zip(fingerprint1, fingerprint2))
                similarity = 1.0 - (differences / len(fingerprint1))
                return similarity
            else:
                # Use Levenshtein distance for different length fingerprints
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, fingerprint1, fingerprint2).ratio()
                return similarity
                
        except Exception as e:
            logger.error(f"Fingerprint similarity calculation failed: {str(e)}")
            return 0.0

    def _score_to_threat_level(self, score: float) -> BrandThreatLevel:
        """Convert violation score to threat level"""
        if score >= 0.9:
            return BrandThreatLevel.CRITICAL
        elif score >= 0.8:
            return BrandThreatLevel.HIGH
        elif score >= 0.6:
            return BrandThreatLevel.MEDIUM
        elif score >= 0.3:
            return BrandThreatLevel.LOW
        else:
            return BrandThreatLevel.NONE

    def _calculate_legal_risk(self, violation_score: float, platform: str) -> float:
        """
Calculate legal risk score based on violation and platform"""
        base_risk = violation_score * 0.8
        
        # Platform-specific risk multipliers
        platform_multipliers = {
            "web": 1.0,
            "amazon": 1.2,
            "ebay": 1.1,
            "alibaba": 1.3,
            "instagram": 0.9,
            "facebook": 0.9,
            "twitter": 0.8
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        return min(base_risk * multiplier, 1.0)

    def _generate_recommended_actions(self, violation_score: float, platform: str) -> List[str]:
        """Generate recommended actions based on violation severity"""
        actions = []
        
        if violation_score >= 0.9:
            actions.extend([
                "Immediate cease and desist letter",
                "Legal consultation required",
                "Document all evidence",
                "Consider emergency injunction"
            ])
        elif violation_score >= 0.7:
            actions.extend([
                "Send formal takedown notice",
                "Contact platform for removal",
                "Monitor for compliance",
                "Prepare legal documentation"
            ])
        elif violation_score >= 0.5:
            actions.extend([
                "Send warning notice",
                "Request voluntary removal",
                "Monitor situation"
            ])
        else:
            actions.extend([
                "Continue monitoring",
                "Document for reference"
            ])
            
        return actions

    async def _prioritize_violations(self, violations: List[BrandViolation]) -> List[BrandViolation]:
        """Prioritize violations based on threat level and impact"""
        try:
            # Sort by threat level, then by confidence score
            priority_order = {
                BrandThreatLevel.CRITICAL: 5,
                BrandThreatLevel.HIGH: 4,
                BrandThreatLevel.MEDIUM: 3,
                BrandThreatLevel.LOW: 2,
                BrandThreatLevel.NONE: 1
            }
            
            sorted_violations = sorted(
                violations,
                key=lambda v: (priority_order[v.threat_level], v.confidence_score),
                reverse=True
            )
            
            return sorted_violations
            
        except Exception as e:
            logger.error(f"Violation prioritization failed: {str(e)}")
            return violations

    def _violation_to_dict(self, violation: BrandViolation) -> Dict[str, Any]:
        """Convert BrandViolation to dictionary for JSON serialization"""
        return {
            "violation_id": violation.violation_id,
            "asset_id": violation.asset_id,
            "violation_type": violation.violation_type.value,
            "threat_level": violation.threat_level.value,
            "confidence_score": violation.confidence_score,
            "detected_at": violation.detected_at.isoformat(),
            "source_url": violation.source_url,
            "source_platform": violation.source_platform,
            "evidence": violation.evidence,
            "similarity_score": violation.similarity_score,
            "legal_risk_score": violation.legal_risk_score,
            "recommended_actions": violation.recommended_actions
        }


class BrandAgentManager:
    """
    Brand Agent Manager - Orchestrates multiple brand agents and monitoring tasks
    
    Provides centralized management for brand protection operations,
    scheduled monitoring, and violation response automation.
    """
    def __init__(self):
        self.agents: Dict[str, BrandAgent] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.violation_handlers: Dict[str, Callable] = {}
        
        logger.info("Brand Agent Manager initialized")

    async def create_agent(self, brand_id: str, config: Dict[str, Any]) -> BrandAgent:
        """Create and configure a new brand agent"""
        try:
            agent_id = f"brand_agent_{brand_id}"
            agent = BrandAgent(agent_id)
            
            # Configure agent with brand-specific settings
            await self._configure_agent(agent, config)
            
            self.agents[brand_id] = agent
            logger.info(f"Brand agent created for brand: {brand_id}")
            
            return agent
            
        except Exception as e:
            logger.error(f"Brand agent creation failed: {str(e)}")
            raise

    async def start_monitoring(self, brand_id: str, monitoring_config: Dict[str, Any]) -> None:
        """Start continuous brand monitoring"""
        try:
            if brand_id not in self.agents:
                raise ValueError(f"No agent found for brand: {brand_id}")
            
            agent = self.agents[brand_id]
            
            # Create monitoring task
            task = asyncio.create_task(
                self._continuous_monitoring(agent, monitoring_config)
            )
            
            self.monitoring_tasks[brand_id] = task
            logger.info(f"Brand monitoring started for: {brand_id}")
            
        except Exception as e:
            logger.error(f"Brand monitoring startup failed: {str(e)}")
            raise

    async def stop_monitoring(self, brand_id: str) -> None:
        """Stop brand monitoring for specific brand"""
        try:
            if brand_id in self.monitoring_tasks:
                task = self.monitoring_tasks[brand_id]
                task.cancel()
                del self.monitoring_tasks[brand_id]
                logger.info(f"Brand monitoring stopped for: {brand_id}")
                
        except Exception as e:
            logger.error(f"Brand monitoring stop failed: {str(e)}")

    async def _configure_agent(self, agent: BrandAgent, config: Dict[str, Any]) -> None:
        """Configure brand agent with specific settings"""
        try:
            # Set monitoring parameters
            agent.monitoring_interval = config.get("monitoring_interval", 3600)  # 1 hour
            agent.violation_threshold = config.get("violation_threshold", 0.7)
            agent.auto_takedown_enabled = config.get("auto_takedown_enabled", False)
            
            # Configure protected assets
            protected_assets = config.get("protected_assets", [])
            for asset_config in protected_assets:
                await agent._register_brand_asset(asset_config)
                
        except Exception as e:
            logger.error(f"Agent configuration failed: {str(e)}")
            raise

    async def _continuous_monitoring(self, agent: BrandAgent, config: Dict[str, Any]) -> None:
        """Continuous monitoring task for brand protection"""
        try:
            monitoring_interval = config.get("monitoring_interval", 3600)
            
            while True:
                try:
                    # Perform violation detection
                    detection_request = AgentRequest(
                        action="detect_violations",
                        data=config.get("search_params", {}),
                        priority=AgentPriority.NORMAL
                    )
                    
                    result = await agent.process_request(detection_request)
                    
                    if result.get("success"):
                        violations = result.get("result", {}).get("violations", [])
                        
                        # Process high-priority violations
                        high_priority = [v for v in violations 
                                       if v.get("threat_level") in ["high", "critical"]]
                        
                        if high_priority:
                            await self._handle_high_priority_violations(agent, high_priority)
                    
                    # Wait for next monitoring cycle
                    await asyncio.sleep(monitoring_interval)
                    
                except asyncio.CancelledError:
                    logger.info(f"Brand monitoring cancelled for agent: {agent.agent_id}")
                    break
                except Exception as e:
                    logger.error(f"Monitoring cycle error: {str(e)}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
                    
        except Exception as e:
            logger.error(f"Continuous monitoring failed: {str(e)}")

    async def _handle_high_priority_violations(self, agent: BrandAgent, violations: List[Dict[str, Any]]) -> None:
        """Handle high-priority brand violations"""
        try:
            for violation in violations:
                threat_level = violation.get("threat_level")
                
                if threat_level == "critical":
                    # Immediate action required
                    await self._handle_critical_violation(agent, violation)
                elif threat_level == "high":
                    # High priority action
                    await self._handle_high_violation(agent, violation)
                    
        except Exception as e:
            logger.error(f"High priority violation handling failed: {str(e)}")

    async def _handle_critical_violation(self, agent: BrandAgent, violation: Dict[str, Any]) -> None:
        """Handle critical brand violations with immediate response"""
        try:
            # Automatically submit takedown request if enabled
            if getattr(agent, 'auto_takedown_enabled', False):
                takedown_request = AgentRequest(
                    action="submit_takedown_request",
                    data={
                        "violation_id": violation.get("violation_id"),
                        "priority": "critical",
                        "auto_escalate": True
                    },
                    priority=AgentPriority.CRITICAL
                )
                
                await agent.process_request(takedown_request)
            
            # Send immediate notifications
            await self._send_critical_alert(violation)
            
        except Exception as e:
            logger.error(f"Critical violation handling failed: {str(e)}")

    async def _send_critical_alert(self, violation: Dict[str, Any]) -> None:
        """Send critical brand violation alert"""
        try:
            # This would integrate with notification systems
            # Email, SMS, Slack, etc.
            logger.critical(f"CRITICAL BRAND VIOLATION DETECTED: {violation.get('violation_id')}")
            
        except Exception as e:
            logger.error(f"Critical alert sending failed: {str(e)}")

    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all brand agents"""
        status = {}
        
        for brand_id, agent in self.agents.items():
            status[brand_id] = {
                "agent_id": agent.agent_id,
                "status": agent.status.value,
                "total_requests": agent.metrics.total_requests,
                "success_rate": (agent.metrics.successful_requests / max(agent.metrics.total_requests, 1)) * 100,
                "monitoring_active": brand_id in self.monitoring_tasks,
                "last_activity": agent.metrics.last_request_time.isoformat() if agent.metrics.last_request_time else None
            }
        
        return status
