"""
Consistency Checker - Advanced Brand Consistency & Style Guardian System

Comprehensive brand consistency analysis across all touchpoints and platforms.
Ensures brand guidelines compliance and maintains visual/textual coherence.

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
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageColor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import webcolors
import colorsys
from pathlib import Path
import requests

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

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
from ...utils.image_analysis import ColorAnalyzer, FontDetector, LayoutAnalyzer
from ...utils.text_analysis import TextStyleAnalyzer, ToneAnalyzer
from ...utils.brand_guidelines import BrandGuidelinesManager
from ...content_protection.fingerprinting import VisualFingerprinter

logger = logging.getLogger(__name__)

class ConsistencyLevel(Enum):
    """Brand consistency levels"""
    PERFECT = "perfect"        # 95-100%
    EXCELLENT = "excellent"    # 85-94%
    GOOD = "good"             # 70-84%
    FAIR = "fair"             # 55-69%
    POOR = "poor"             # 40-54%
    CRITICAL = "critical"      # <40%

class ConsistencyArea(Enum):
    """Areas of brand consistency"""
    VISUAL_IDENTITY = "visual_identity"
    COLOR_PALETTE = "color_palette"
    TYPOGRAPHY = "typography"
    LOGO_USAGE = "logo_usage"
    IMAGERY_STYLE = "imagery_style"
    TONE_OF_VOICE = "tone_of_voice"
    MESSAGING = "messaging"
    LAYOUT_DESIGN = "layout_design"

class ViolationType(Enum):
    """Types of consistency violations"""
    COLOR_DEVIATION = "color_deviation"
    FONT_MISMATCH = "font_mismatch"
    LOGO_MISUSE = "logo_misuse"
    TONE_INCONSISTENCY = "tone_inconsistency"
    MESSAGE_CONTRADICTION = "message_contradiction"
    LAYOUT_VIOLATION = "layout_violation"
    SPACING_ERROR = "spacing_error"
    PROPORTION_ERROR = "proportion_error"

@dataclass
class BrandGuidelines:
    """Comprehensive brand guidelines definition"""
    brand_id: str
    
    # Visual Guidelines
    primary_colors: List[str] = field(default_factory=list)
    secondary_colors: List[str] = field(default_factory=list)
    accent_colors: List[str] = field(default_factory=list)
    color_tolerances: Dict[str, float] = field(default_factory=lambda: {"primary": 5.0, "secondary": 10.0})
    
    # Typography Guidelines
    primary_fonts: List[str] = field(default_factory=list)
    secondary_fonts: List[str] = field(default_factory=list)
    font_sizes: Dict[str, int] = field(default_factory=dict)
    line_heights: Dict[str, float] = field(default_factory=dict)
    font_weights: Dict[str, str] = field(default_factory=dict)
    
    # Logo Guidelines
    logo_variations: List[str] = field(default_factory=list)
    logo_min_size: int = 50
    logo_clear_space: int = 20
    logo_prohibited_uses: List[str] = field(default_factory=list)
    
    # Voice & Tone Guidelines
    tone_attributes: List[str] = field(default_factory=list)  # friendly, professional, casual
    voice_characteristics: Dict[str, Any] = field(default_factory=dict)
    prohibited_language: List[str] = field(default_factory=list)
    key_messages: List[str] = field(default_factory=list)
    
    # Layout Guidelines
    grid_system: Dict[str, Any] = field(default_factory=dict)
    spacing_rules: Dict[str, int] = field(default_factory=dict)
    alignment_rules: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConsistencyViolation:
    """Brand consistency violation record"""
    violation_id: str
    brand_id: str
    violation_type: ViolationType
    area: ConsistencyArea
    severity: str  # low, medium, high, critical
    confidence: float
    detected_at: datetime
    
    # Content details
    content_url: Optional[str] = None
    content_type: str = "unknown"  # image, text, video, webpage
    platform: Optional[str] = None
    
    # Violation specifics
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    deviation_amount: Optional[float] = None
    
    # Evidence
    screenshot_path: Optional[str] = None
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    
    # Resolution
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    fixed_at: Optional[datetime] = None

@dataclass
class ConsistencyReport:
    """Comprehensive brand consistency analysis report"""
    report_id: str
    brand_id: str
    overall_score: float
    consistency_level: ConsistencyLevel
    
    # Area-specific scores
    area_scores: Dict[str, float] = field(default_factory=dict)
    
    # Violations
    violations: List[ConsistencyViolation] = field(default_factory=list)
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    
    # Analysis details
    content_analyzed: int = 0
    platforms_checked: List[str] = field(default_factory=list)
    
    # Recommendations
    priority_fixes: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    generated_at: datetime = field(default_factory=datetime.utcnow)

class ConsistencyChecker:
    """
    Advanced Brand Consistency & Style Guardian System
    
    Comprehensive brand consistency analysis including:
    - Visual identity consistency across platforms
    - Color palette compliance checking
    - Typography and font usage validation
    - Logo usage compliance monitoring
    - Tone of voice consistency analysis
    - Layout and design guideline enforcement
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.guidelines: Optional[BrandGuidelines] = None
        
        # Initialize analysis tools
        self.color_analyzer = ColorAnalyzer()
        self.font_detector = FontDetector()
        self.layout_analyzer = LayoutAnalyzer()
        self.text_style_analyzer = TextStyleAnalyzer()
        self.tone_analyzer = ToneAnalyzer()
        self.visual_fingerprinter = VisualFingerprinter()
        self.guidelines_manager = BrandGuidelinesManager()
        
        # NLP model for text analysis
        self.nlp = spacy.load("en_core_web_lg")
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Consistency tracking
        self.consistency_history: List[ConsistencyReport] = []
        self.violation_patterns: Dict[str, int] = {}
        
        logger.info(f"Consistency checker initialized for brand: {brand_id}")

    async def load_brand_guidelines(self, guidelines_config: Dict[str, Any]) -> None:
        """Load and configure brand guidelines"""
        try:
            self.guidelines = BrandGuidelines(
                brand_id=self.brand_id,
                primary_colors=guidelines_config.get("primary_colors", []),
                secondary_colors=guidelines_config.get("secondary_colors", []),
                accent_colors=guidelines_config.get("accent_colors", []),
                color_tolerances=guidelines_config.get("color_tolerances", {}),
                primary_fonts=guidelines_config.get("primary_fonts", []),
                secondary_fonts=guidelines_config.get("secondary_fonts", []),
                font_sizes=guidelines_config.get("font_sizes", {}),
                logo_variations=guidelines_config.get("logo_variations", []),
                logo_min_size=guidelines_config.get("logo_min_size", 50),
                logo_clear_space=guidelines_config.get("logo_clear_space", 20),
                tone_attributes=guidelines_config.get("tone_attributes", []),
                voice_characteristics=guidelines_config.get("voice_characteristics", {}),
                prohibited_language=guidelines_config.get("prohibited_language", []),
                key_messages=guidelines_config.get("key_messages", []),
                grid_system=guidelines_config.get("grid_system", {}),
                spacing_rules=guidelines_config.get("spacing_rules", {}),
                alignment_rules=guidelines_config.get("alignment_rules", [])
            )
            
            logger.info(f"Brand guidelines loaded: {len(self.guidelines.primary_colors)} primary colors, {len(self.guidelines.primary_fonts)} fonts")
            
        except Exception as e:
            logger.error(f"Brand guidelines loading failed: {str(e)}")
            raise

    async def check_content_consistency(self, content_items: List[Dict[str, Any]]) -> ConsistencyReport:
        """Check consistency across multiple content items"""
        try:
            if not self.guidelines:
                raise ValueError("Brand guidelines not loaded")
            
            report_id = f"consistency_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting consistency check: {report_id}")
            
            violations = []
            area_scores = {}
            
            # Analyze each content item
            for item in content_items:
                item_violations = await self._analyze_content_item(item)
                violations.extend(item_violations)
            
            # Calculate area-specific scores
            for area in ConsistencyArea:
                area_violations = [v for v in violations if v.area == area]
                area_scores[area.value] = await self._calculate_area_score(area_violations, len(content_items))
            
            # Calculate overall score
            overall_score = sum(area_scores.values()) / len(area_scores) if area_scores else 0
            consistency_level = self._score_to_level(overall_score)
            
            # Count violations by severity
            violation_counts = self._count_violations_by_severity(violations)
            
            # Generate recommendations
            priority_fixes = await self._generate_priority_fixes(violations)
            improvement_suggestions = await self._generate_improvement_suggestions(area_scores)
            
            # Create report
            report = ConsistencyReport(
                report_id=report_id,
                brand_id=self.brand_id,
                overall_score=overall_score,
                consistency_level=consistency_level,
                area_scores=area_scores,
                violations=violations,
                critical_violations=violation_counts["critical"],
                high_violations=violation_counts["high"],
                medium_violations=violation_counts["medium"],
                low_violations=violation_counts["low"],
                content_analyzed=len(content_items),
                platforms_checked=list(set([item.get("platform", "unknown") for item in content_items])),
                priority_fixes=priority_fixes,
                improvement_suggestions=improvement_suggestions
            )
            
            self.consistency_history.append(report)
            
            logger.info(f"Consistency check completed. Overall score: {overall_score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"Consistency check failed: {str(e)}")
            raise

    async def _analyze_content_item(self, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Analyze individual content item for consistency violations"""
        violations = []
        
        try:
            content_type = item.get("type", "unknown")
            content_url = item.get("url")
            platform = item.get("platform")
            
            if content_type in ["image", "webpage", "social_post"]:
                # Visual content analysis
                visual_violations = await self._check_visual_consistency(item)
                violations.extend(visual_violations)
                
            if content_type in ["text", "webpage", "social_post", "article"]:
                # Text content analysis
                text_violations = await self._check_text_consistency(item)
                violations.extend(text_violations)
                
            if content_type == "webpage":
                # Layout analysis for web pages
                layout_violations = await self._check_layout_consistency(item)
                violations.extend(layout_violations)
                
        except Exception as e:
            logger.error(f"Content item analysis failed: {str(e)}")
            
        return violations

    async def _check_visual_consistency(self, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check visual consistency of content item"""
        violations = []
        
        try:
            image_path = item.get("file_path") or item.get("url")
            if not image_path:
                return violations
            
            # Download image if URL
            if image_path.startswith("http"):
                image_path = await self._download_image_for_analysis(image_path)
            
            if not image_path or not Path(image_path).exists():
                return violations
            
            # Color consistency check
            color_violations = await self._check_color_consistency(image_path, item)
            violations.extend(color_violations)
            
            # Font consistency check
            font_violations = await self._check_font_consistency(image_path, item)
            violations.extend(font_violations)
            
            # Logo usage check
            logo_violations = await self._check_logo_consistency(image_path, item)
            violations.extend(logo_violations)
            
            # Layout consistency check
            layout_violations = await self._check_visual_layout_consistency(image_path, item)
            violations.extend(layout_violations)
            
        except Exception as e:
            logger.error(f"Visual consistency check failed: {str(e)}")
            
        return violations

    async def _check_color_consistency(self, image_path: str, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check color palette consistency"""
        violations = []
        
        try:
            # Extract colors from image
            detected_colors = await self.color_analyzer.extract_dominant_colors(image_path)
            
            # Check primary colors compliance
            primary_violations = await self._check_primary_colors_usage(detected_colors, item)
            violations.extend(primary_violations)
            
            # Check for prohibited color combinations
            combination_violations = await self._check_color_combinations(detected_colors, item)
            violations.extend(combination_violations)
            
            # Check color harmony
            harmony_violations = await self._check_color_harmony(detected_colors, item)
            violations.extend(harmony_violations)
            
        except Exception as e:
            logger.error(f"Color consistency check failed: {str(e)}")
            
        return violations

    async def _check_primary_colors_usage(self, detected_colors: List[str], item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check if primary brand colors are used correctly"""
        violations = []
        
        try:
            if not self.guidelines.primary_colors:
                return violations
            
            # Calculate color distances
            brand_colors_used = 0
            color_deviations = []
            
            for detected_color in detected_colors:
                closest_brand_color = None
                min_distance = float('inf')
                
                for brand_color in self.guidelines.primary_colors:
                    distance = self._calculate_color_distance(detected_color, brand_color)
                    if distance < min_distance:
                        min_distance = distance
                        closest_brand_color = brand_color
                
                # Check if within tolerance
                tolerance = self.guidelines.color_tolerances.get("primary", 5.0)
                if min_distance <= tolerance:
                    brand_colors_used += 1
                elif min_distance <= tolerance * 3:  # Close but not exact
                    color_deviations.append({
                        "detected": detected_color,
                        "expected": closest_brand_color,
                        "distance": min_distance
                    })
            
            # Create violations for significant deviations
            for deviation in color_deviations:
                if deviation["distance"] > self.guidelines.color_tolerances.get("primary", 5.0):
                    violation = ConsistencyViolation(
                        violation_id=f"color_{hashlib.md5(f'{item.get(\"url\", \"\")}_{deviation[\"detected\"]}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}",
                        brand_id=self.brand_id,
                        violation_type=ViolationType.COLOR_DEVIATION,
                        area=ConsistencyArea.COLOR_PALETTE,
                        severity=self._deviation_to_severity(deviation["distance"]),
                        confidence=0.8,
                        detected_at=datetime.utcnow(),
                        content_url=item.get("url"),
                        content_type=item.get("type", "unknown"),
                        platform=item.get("platform"),
                        expected_value=deviation["expected"],
                        actual_value=deviation["detected"],
                        deviation_amount=deviation["distance"],
                        suggested_fix=f"Use brand color {deviation['expected']} instead of {deviation['detected']}"
                    )
                    violations.append(violation)
                    
        except Exception as e:
            logger.error(f"Primary colors check failed: {str(e)}")
            
        return violations

    def _calculate_color_distance(self, color1: str, color2: str) -> float:
        """Calculate perceptual distance between two colors"""
        try:
            # Convert hex to RGB
            rgb1 = self._hex_to_rgb(color1)
            rgb2 = self._hex_to_rgb(color2)
            
            # Convert to LAB color space for perceptual distance
            lab1 = self._rgb_to_lab(rgb1)
            lab2 = self._rgb_to_lab(rgb2)
            
            # Calculate Delta E (CIE76)
            delta_e = ((lab1[0] - lab2[0]) ** 2 + 
                      (lab1[1] - lab2[1]) ** 2 + 
                      (lab1[2] - lab2[2]) ** 2) ** 0.5
            
            return delta_e
            
        except Exception:
            # Fallback to simple RGB distance
            rgb1 = self._hex_to_rgb(color1)
            rgb2 = self._hex_to_rgb(color2)
            
            return ((rgb1[0] - rgb2[0]) ** 2 + 
                   (rgb1[1] - rgb2[1]) ** 2 + 
                   (rgb1[2] - rgb2[2]) ** 2) ** 0.5

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_lab(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to LAB color space (simplified)"""
        # Normalize RGB values
        r, g, b = [x / 255.0 for x in rgb]
        
        # Convert to XYZ (simplified sRGB to XYZ)
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        
        # Convert XYZ to LAB (simplified)
        l = 116 * (y ** (1/3)) - 16 if y > 0.008856 else 903.3 * y
        a = 500 * ((x ** (1/3)) - (y ** (1/3))) if x > 0.008856 and y > 0.008856 else 0
        b_lab = 200 * ((y ** (1/3)) - (z ** (1/3))) if y > 0.008856 and z > 0.008856 else 0
        
        return (l, a, b_lab)

    def _deviation_to_severity(self, deviation: float) -> str:
        """Convert deviation amount to severity level"""
        if deviation >= 50:
            return "critical"
        elif deviation >= 30:
            return "high"
        elif deviation >= 15:
            return "medium"
        else:
            return "low"

    async def _check_font_consistency(self, image_path: str, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check font and typography consistency"""
        violations = []
        
        try:
            # Detect fonts in image
            detected_fonts = await self.font_detector.detect_fonts_in_image(image_path)
            
            if not detected_fonts:
                return violations
            
            # Check against brand font guidelines
            for detected_font in detected_fonts:
                font_name = detected_font.get("font_family", "unknown")
                font_size = detected_font.get("font_size", 0)
                
                # Check if font is approved
                is_approved = (font_name in self.guidelines.primary_fonts or 
                             font_name in self.guidelines.secondary_fonts)
                
                if not is_approved:
                    # Check for similar approved fonts
                    similar_font = self._find_similar_approved_font(font_name)
                    
                    violation = ConsistencyViolation(
                        violation_id=f"font_{hashlib.md5(f'{item.get(\"url\", \"\")}_{font_name}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}",
                        brand_id=self.brand_id,
                        violation_type=ViolationType.FONT_MISMATCH,
                        area=ConsistencyArea.TYPOGRAPHY,
                        severity="medium" if similar_font else "high",
                        confidence=0.7,
                        detected_at=datetime.utcnow(),
                        content_url=item.get("url"),
                        content_type=item.get("type", "unknown"),
                        platform=item.get("platform"),
                        expected_value=similar_font or "approved brand font",
                        actual_value=font_name,
                        suggested_fix=f"Replace {font_name} with {similar_font or 'an approved brand font'}"
                    )
                    violations.append(violation)
                    
                # Check font size compliance
                if font_size > 0:
                    size_violations = await self._check_font_size_compliance(font_size, detected_font, item)
                    violations.extend(size_violations)
                    
        except Exception as e:
            logger.error(f"Font consistency check failed: {str(e)}")
            
        return violations

    def _find_similar_approved_font(self, font_name: str) -> Optional[str]:
        """Find similar approved font for suggestion"""
        try:
            all_approved = self.guidelines.primary_fonts + self.guidelines.secondary_fonts
            
            font_name_lower = font_name.lower()
            
            # Check for partial matches
            for approved_font in all_approved:
                if (font_name_lower in approved_font.lower() or 
                    approved_font.lower() in font_name_lower):
                    return approved_font
            
            # Font family groupings
            font_families = {
                "sans-serif": ["arial", "helvetica", "opensans", "roboto", "lato"],
                "serif": ["times", "georgia", "garamond", "playfair"],
                "monospace": ["courier", "monaco", "consolas", "sourcecodepro"]
            }
            
            for family_type, family_fonts in font_families.items():
                if any(family_font in font_name_lower for family_font in family_fonts):
                    # Find approved font from same family
                    for approved_font in all_approved:
                        if any(family_font in approved_font.lower() for family_font in family_fonts):
                            return approved_font
            
            return None
            
        except Exception:
            return None

    async def _check_text_consistency(self, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check text content consistency"""
        violations = []
        
        try:
            text_content = item.get("text") or item.get("content", "")
            if not text_content:
                return violations
            
            # Tone of voice analysis
            tone_violations = await self._check_tone_consistency(text_content, item)
            violations.extend(tone_violations)
            
            # Message consistency check
            message_violations = await self._check_message_consistency(text_content, item)
            violations.extend(message_violations)
            
            # Language and style check
            style_violations = await self._check_style_consistency(text_content, item)
            violations.extend(style_violations)
            
        except Exception as e:
            logger.error(f"Text consistency check failed: {str(e)}")
            
        return violations

    async def _check_tone_consistency(self, text: str, item: Dict[str, Any]) -> List[ConsistencyViolation]:
        """Check tone of voice consistency"""
        violations = []
        
        try:
            if not self.guidelines.tone_attributes:
                return violations
            
            # Analyze text tone
            tone_analysis = await self.tone_analyzer.analyze_tone(text)
            detected_attributes = tone_analysis.get("attributes", [])
            confidence = tone_analysis.get("confidence", 0.5)
            
            # Check alignment with brand tone
            mismatched_attributes = []
            for brand_attribute in self.guidelines.tone_attributes:
                if brand_attribute not in detected_attributes:
                    # Check if opposite attribute is present
                    opposite_attribute = self._get_opposite_tone_attribute(brand_attribute)
                    if opposite_attribute in detected_attributes:
                        mismatched_attributes.append({
                            "expected": brand_attribute,
                            "detected": opposite_attribute
                        })
            
            # Create violations for tone mismatches
            for mismatch in mismatched_attributes:
                violation = ConsistencyViolation(
                    violation_id=f"tone_{hashlib.md5(f'{item.get(\"url\", \"\")}_{mismatch[\"expected\"]}_{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}",
                    brand_id=self.brand_id,
                    violation_type=ViolationType.TONE_INCONSISTENCY,
                    area=ConsistencyArea.TONE_OF_VOICE,
                    severity="medium",
                    confidence=confidence,
                    detected_at=datetime.utcnow(),
                    content_url=item.get("url"),
                    content_type=item.get("type", "unknown"),
                    platform=item.get("platform"),
                    expected_value=mismatch["expected"],
                    actual_value=mismatch["detected"],
                    suggested_fix=f"Adjust tone to be more {mismatch['expected']} and less {mismatch['detected']}"
                )
                violations.append(violation)
                
        except Exception as e:
            logger.error(f"Tone consistency check failed: {str(e)}")
            
        return violations

    def _get_opposite_tone_attribute(self, attribute: str) -> str:
        """Get opposite tone attribute for comparison"""
        opposites = {
            "friendly": "hostile",
            "professional": "casual",
            "formal": "informal",
            "serious": "playful",
            "authoritative": "humble",
            "energetic": "calm",
            "confident": "uncertain",
            "warm": "cold",
            "innovative": "traditional",
            "trustworthy": "suspicious"
        }
        
        return opposites.get(attribute.lower(), "inconsistent")

    async def _calculate_area_score(self, violations: List[ConsistencyViolation], total_content: int) -> float:
        """Calculate consistency score for specific area"""
        try:
            if total_content == 0:
                return 100.0
            
            # Weight violations by severity
            severity_weights = {
                "critical": 10,
                "high": 5,
                "medium": 2,
                "low": 1
            }
            
            total_penalty = 0
            for violation in violations:
                weight = severity_weights.get(violation.severity, 1)
                total_penalty += weight
            
            # Calculate score (higher penalty = lower score)
            max_possible_penalty = total_content * severity_weights["critical"]
            score = max(0, 100 - (total_penalty / max_possible_penalty * 100))
            
            return score
            
        except Exception as e:
            logger.error(f"Area score calculation failed: {str(e)}")
            return 50.0

    def _score_to_level(self, score: float) -> ConsistencyLevel:
        """Convert numeric score to consistency level"""
        if score >= 95:
            return ConsistencyLevel.PERFECT
        elif score >= 85:
            return ConsistencyLevel.EXCELLENT
        elif score >= 70:
            return ConsistencyLevel.GOOD
        elif score >= 55:
            return ConsistencyLevel.FAIR
        elif score >= 40:
            return ConsistencyLevel.POOR
        else:
            return ConsistencyLevel.CRITICAL

    def _count_violations_by_severity(self, violations: List[ConsistencyViolation]) -> Dict[str, int]:
        """Count violations by severity level"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for violation in violations:
            severity = violation.severity
            if severity in counts:
                counts[severity] += 1
                
        return counts

    async def _generate_priority_fixes(self, violations: List[ConsistencyViolation]) -> List[str]:
        """Generate prioritized list of fixes"""
        priority_fixes = []
        
        try:
            # Sort violations by severity and frequency
            critical_violations = [v for v in violations if v.severity == "critical"]
            high_violations = [v for v in violations if v.severity == "high"]
            
            # Group by violation type to find patterns
            violation_types = {}
            for violation in critical_violations + high_violations:
                vtype = violation.violation_type.value
                if vtype not in violation_types:
                    violation_types[vtype] = []
                violation_types[vtype].append(violation)
            
            # Generate fixes for most common issues first
            sorted_types = sorted(violation_types.items(), key=lambda x: len(x[1]), reverse=True)
            
            for vtype, type_violations in sorted_types[:5]:  # Top 5 issues
                fix_suggestion = await self._generate_type_specific_fix(vtype, type_violations)
                if fix_suggestion:
                    priority_fixes.append(fix_suggestion)
                    
        except Exception as e:
            logger.error(f"Priority fixes generation failed: {str(e)}")
            
        return priority_fixes

    async def _generate_type_specific_fix(self, violation_type: str, violations: List[ConsistencyViolation]) -> Optional[str]:
        """Generate specific fix for violation type"""
        try:
            count = len(violations)
            
            if violation_type == "color_deviation":
                most_common_expected = max(set([v.expected_value for v in violations if v.expected_value]), 
                                         key=[v.expected_value for v in violations if v.expected_value].count)
                return f"Fix {count} color deviations by using brand color {most_common_expected}"
                
            elif violation_type == "font_mismatch":
                return f"Replace {count} non-brand fonts with approved typography"
                
            elif violation_type == "tone_inconsistency":
                return f"Adjust tone of voice in {count} pieces of content to match brand guidelines"
                
            elif violation_type == "logo_misuse":
                return f"Correct {count} logo usage violations according to brand guidelines"
                
            else:
                return f"Address {count} {violation_type.replace('_', ' ')} issues"
                
        except Exception as e:
            logger.error(f"Type-specific fix generation failed: {str(e)}")
            return None

    async def monitor_brand_consistency(self, monitoring_config: Dict[str, Any]) -> None:
        """Start continuous brand consistency monitoring"""
        try:
            platforms = monitoring_config.get("platforms", [])
            check_interval = monitoring_config.get("interval", 3600)  # 1 hour default
            
            while True:
                try:
                    # Collect recent content from monitored platforms
                    content_items = await self._collect_recent_content(platforms)
                    
                    if content_items:
                        # Perform consistency check
                        report = await self.check_content_consistency(content_items)
                        
                        # Alert on critical violations
                        if report.critical_violations > 0:
                            await self._send_consistency_alert(report)
                    
                    await asyncio.sleep(check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Consistency monitoring cycle error: {str(e)}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
                    
        except Exception as e:
            logger.error(f"Brand consistency monitoring failed: {str(e)}")

    async def generate_style_guide_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive style guide compliance report"""
        try:
            if not self.consistency_history:
                return {"error": "No consistency data available"}
            
            latest_report = self.consistency_history[-1]
            
            # Calculate compliance trends
            compliance_trend = await self._calculate_compliance_trend()
            
            # Identify recurring issues
            recurring_issues = await self._identify_recurring_issues()
            
            # Generate improvement recommendations
            improvement_plan = await self._generate_improvement_plan()
            
            return {
                "current_compliance": {
                    "overall_score": latest_report.overall_score,
                    "level": latest_report.consistency_level.value,
                    "area_scores": latest_report.area_scores
                },
                "compliance_trend": compliance_trend,
                "recurring_issues": recurring_issues,
                "improvement_plan": improvement_plan,
                "critical_actions": latest_report.priority_fixes,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Style guide compliance report generation failed: {str(e)}")
            return {"error": str(e)}


class StyleGuardian:
    """
    Advanced Style Guardian System
    
    Real-time brand style monitoring and enforcement across all digital touchpoints.
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.consistency_checker = ConsistencyChecker(brand_id)
        self.auto_fix_enabled = False
        self.monitoring_active = False
        
        # Style enforcement rules
        self.enforcement_rules: Dict[str, Any] = {}
        self.violation_thresholds: Dict[str, float] = {
            "critical": 0.1,    # 10% critical violations trigger immediate action
            "high": 0.3,        # 30% high violations trigger alert
            "medium": 0.5       # 50% medium violations trigger warning
        }
        
        logger.info(f"Style guardian initialized for brand: {brand_id}")

    async def configure_enforcement_rules(self, rules_config: Dict[str, Any]) -> None:
        """Configure style enforcement rules and automation"""
        try:
            self.enforcement_rules = rules_config
            self.auto_fix_enabled = rules_config.get("auto_fix_enabled", False)
            self.violation_thresholds.update(rules_config.get("violation_thresholds", {}))
            
            logger.info(f"Style enforcement configured. Auto-fix: {self.auto_fix_enabled}")
            
        except Exception as e:
            logger.error(f"Enforcement rules configuration failed: {str(e)}")
            raise

    async def enforce_style_compliance(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce style compliance on content item"""
        try:
            # Check compliance
            violations = await self.consistency_checker._analyze_content_item(content_item)
            
            # Categorize violations
            critical_violations = [v for v in violations if v.severity == "critical"]
            auto_fixable_violations = [v for v in violations if v.auto_fixable]
            
            result = {
                "compliant": len(critical_violations) == 0,
                "total_violations": len(violations),
                "critical_violations": len(critical_violations),
                "auto_fixable": len(auto_fixable_violations),
                "fixes_applied": []
            }
            
            # Apply automatic fixes if enabled
            if self.auto_fix_enabled and auto_fixable_violations:
                fixes_applied = await self._apply_automatic_fixes(content_item, auto_fixable_violations)
                result["fixes_applied"] = fixes_applied
            
            return result
            
        except Exception as e:
            logger.error(f"Style compliance enforcement failed: {str(e)}")
            return {"compliant": False, "error": str(e)}

    async def _apply_automatic_fixes(self, content_item: Dict[str, Any], violations: List[ConsistencyViolation]) -> List[str]:
        """Apply automatic fixes to violations"""
        fixes_applied = []
        
        try:
            for violation in violations:
                if violation.violation_type == ViolationType.COLOR_DEVIATION:
                    fix_applied = await self._auto_fix_color_deviation(content_item, violation)
                    if fix_applied:
                        fixes_applied.append(f"Fixed color deviation: {violation.actual_value} -> {violation.expected_value}")
                        
                elif violation.violation_type == ViolationType.FONT_MISMATCH:
                    fix_applied = await self._auto_fix_font_mismatch(content_item, violation)
                    if fix_applied:
                        fixes_applied.append(f"Fixed font mismatch: {violation.actual_value} -> {violation.expected_value}")
                        
        except Exception as e:
            logger.error(f"Automatic fixes application failed: {str(e)}")
            
        return fixes_applied

    def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for compliance dashboard"""
        try:
            if not self.consistency_checker.consistency_history:
                return {"status": "no_data"}
            
            latest_report = self.consistency_checker.consistency_history[-1]
            
            return {
                "overall_compliance": latest_report.overall_score,
                "compliance_level": latest_report.consistency_level.value,
                "area_breakdown": latest_report.area_scores,
                "violation_summary": {
                    "critical": latest_report.critical_violations,
                    "high": latest_report.high_violations,
                    "medium": latest_report.medium_violations,
                    "low": latest_report.low_violations
                },
                "platforms_monitored": latest_report.platforms_checked,
                "last_updated": latest_report.generated_at.isoformat(),
                "trending": self._calculate_compliance_trend_indicator()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _calculate_compliance_trend_indicator(self) -> str:
        """Calculate compliance trend indicator"""
        try:
            if len(self.consistency_checker.consistency_history) < 2:
                return "stable"
            
            current_score = self.consistency_checker.consistency_history[-1].overall_score
            previous_score = self.consistency_checker.consistency_history[-2].overall_score
            
            difference = current_score - previous_score
            
            if difference > 5:
                return "improving"
            elif difference < -5:
                return "declining"
            else:
                return "stable"
                
        except Exception:
            return "unknown"
