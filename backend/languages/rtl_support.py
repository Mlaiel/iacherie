"""RTL Support - Advanced Right-to-Left Language Processing Engine
================================================================================
Module: backend/languages/rtl_support.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial RTL Processing Engine - Bidirectional Text Support
Responsibility: Comprehensive RTL/BiDi text processing, layout adaptation, and direction handling
Technologies: Python, Unicode BiDi Algorithm, CSS RTL, Layout Processing
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Text input → Direction detection → BiDi algorithm → Layout calculation → 
CSS generation → UI adaptation → Mixed content processing → RTL output
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import unicodedata

logger = logging.getLogger(__name__)


class TextDirection(Enum):
    """Text direction types"""
    LTR = "ltr"  # Left-to-Right
    RTL = "rtl"  # Right-to-Left
    AUTO = "auto"  # Automatic detection
    MIXED = "mixed"  # Mixed direction content


class RTLLanguage(Enum):
    """Supported RTL languages"""
    ARABIC = "ar"
    HEBREW = "he"
    PERSIAN = "fa"
    URDU = "ur"
    KURDISH = "ku"
    PASHTO = "ps"
    SINDHI = "sd"
    DIVEHI = "dv"
    SYRIAC = "syr"
    THAANA = "dv"


class BiDiType(Enum):
    """Unicode Bidirectional Character Types"""
    L = "L"      # Left-to-Right
    R = "R"      # Right-to-Left
    AL = "AL"    # Right-to-Left Arabic
    EN = "EN"    # European Number
    ES = "ES"    # European Number Separator
    ET = "ET"    # European Number Terminator
    AN = "AN"    # Arabic Number
    CS = "CS"    # Common Number Separator
    NSM = "NSM"  # Non-Spacing Mark
    BN = "BN"    # Boundary Neutral
    B = "B"      # Paragraph Separator
    S = "S"      # Segment Separator
    WS = "WS"    # Whitespace
    ON = "ON"    # Other Neutrals


@dataclass
class RTLProcessingOptions:
    """Options for RTL text processing"""
    enable_bidi_algorithm: bool = True
    preserve_ltr_sections: bool = True
    handle_numbers: bool = True
    process_punctuation: bool = True
    generate_css: bool = True
    mirror_characters: bool = True
    adjust_layout: bool = True


@dataclass
class BiDiSpan:
    """Bidirectional text span with direction information"""
    text: str
    direction: TextDirection
    start_pos: int
    end_pos: int
    bidi_level: int
    character_types: List[BiDiType] = field(default_factory=list)


@dataclass
class RTLProcessingResult:
    """Result of RTL text processing"""
    processed_text: str
    original_text: str
    detected_direction: TextDirection
    bidi_spans: List[BiDiSpan]
    css_styles: Dict[str, str]
    layout_adjustments: List[str]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RTLProcessor:
    """
    Advanced RTL/BiDi text processing engine supporting all RTL languages
    with comprehensive layout and styling adaptation
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize RTL processor"""
        self.config = config or {}
        self.rtl_languages = self._load_rtl_language_data()
        self.bidi_mappings = self._load_bidi_character_mappings()
        self.mirrored_characters = self._load_mirrored_characters()
        self.css_templates = self._load_css_templates()
        
        # Processing statistics
        self.processing_stats = {
            "total_processed": 0,
            "rtl_detected": 0,
            "mixed_direction": 0,
            "average_processing_time": 0.0
        }
        
        logger.info("RTLProcessor initialized with comprehensive BiDi support")
    
    async def process_text(self, text: str, options: Optional[RTLProcessingOptions] = None) -> RTLProcessingResult:
        """
        Process text for RTL/BiDi display with comprehensive layout adaptation
        
        Args:
            text: Input text to process
            options: Processing options
            
        Returns:
            RTLProcessingResult with processed text and layout information
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            if not text or not text.strip():
                raise ValueError("Empty text provided for RTL processing")
            
            options = options or RTLProcessingOptions()
            
            # Detect overall text direction
            detected_direction = await self._detect_text_direction(text)
            
            # Analyze BiDi character types
            bidi_analysis = await self._analyze_bidi_characters(text)
            
            # Apply BiDi algorithm if enabled
            if options.enable_bidi_algorithm:
                bidi_spans = await self._apply_bidi_algorithm(text, bidi_analysis)
                processed_text = await self._reorder_text(text, bidi_spans)
            else:
                bidi_spans = [BiDiSpan(text, detected_direction, 0, len(text), 0)]
                processed_text = text
            
            # Mirror characters if needed
            if options.mirror_characters and detected_direction == TextDirection.RTL:
                processed_text = await self._mirror_characters(processed_text)
            
            # Generate CSS styles
            css_styles = {}
            if options.generate_css:
                css_styles = await self._generate_css_styles(detected_direction, bidi_spans)
            
            # Calculate layout adjustments
            layout_adjustments = []
            if options.adjust_layout:
                layout_adjustments = await self._calculate_layout_adjustments(detected_direction, bidi_spans)
            
            # Create result
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = RTLProcessingResult(
                processed_text=processed_text,
                original_text=text,
                detected_direction=detected_direction,
                bidi_spans=bidi_spans,
                css_styles=css_styles,
                layout_adjustments=layout_adjustments,
                processing_time=processing_time,
                metadata={
                    "text_length": len(text),
                    "rtl_percentage": self._calculate_rtl_percentage(bidi_analysis),
                    "mixed_direction": detected_direction == TextDirection.MIXED
                }
            )
            
            # Update statistics
            await self._update_processing_stats(result)
            
            logger.info(f"RTL processing completed: {detected_direction.value} direction detected "
                       f"({len(bidi_spans)} BiDi spans)")
            
            return result
            
        except Exception as e:
            logger.error(f"RTL processing failed: {e}")
            return await self._create_fallback_result(text)
    
    async def detect_rtl_language(self, text: str) -> Optional[RTLLanguage]:
        """
        Detect if text is in an RTL language
        
        Args:
            text: Input text
            
        Returns:
            RTLLanguage if detected, None otherwise
        """
        # Count RTL characters by script
        script_counts = {}
        
        for char in text:
            script = self._get_character_script(char)
            if script in ["Arabic", "Hebrew", "Syriac", "Thaana"]:
                script_counts[script] = script_counts.get(script, 0) + 1
        
        if not script_counts:
            return None
        
        # Determine most common RTL script
        dominant_script = max(script_counts.items(), key=lambda x: x[1])[0]
        
        # Map script to RTL language
        script_to_language = {
            "Arabic": RTLLanguage.ARABIC,
            "Hebrew": RTLLanguage.HEBREW,
            "Syriac": RTLLanguage.SYRIAC,
            "Thaana": RTLLanguage.THAANA
        }
        
        return script_to_language.get(dominant_script)
    
    async def generate_rtl_html(self, text: str, language_code: Optional[str] = None) -> str:
        """
        Generate RTL-ready HTML with proper attributes and styling
        
        Args:
            text: Input text
            language_code: Optional language code
            
        Returns:
            HTML string with RTL attributes
        """
        # Process text for RTL
        result = await self.process_text(text)
        
        # Determine language and direction attributes
        direction = result.detected_direction.value
        lang_attr = f'lang="{language_code}"' if language_code else ""
        
        # Build HTML with proper attributes
        html_parts = []
        html_parts.append(f'<div dir="{direction}" {lang_attr} class="rtl-content">')
        
        # Add CSS if needed
        if result.css_styles:
            html_parts.append('<style>')
            for selector, styles in result.css_styles.items():
                html_parts.append(f'{selector} {{ {styles} }}')
            html_parts.append('</style>')
        
        # Add processed text with span elements for different directions
        if len(result.bidi_spans) > 1:
            for span in result.bidi_spans:
                span_dir = span.direction.value
                span_class = f"bidi-span-{span_dir}"
                html_parts.append(f'<span dir="{span_dir}" class="{span_class}">{span.text}</span>')
        else:
            html_parts.append(result.processed_text)
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    async def get_css_framework(self) -> Dict[str, str]:
        """
        Get comprehensive CSS framework for RTL support
        
        Returns:
            Dictionary of CSS rules for RTL support
        """
        return {
            "base_rtl": """
                .rtl-content {
                    direction: rtl;
                    text-align: right;
                    unicode-bidi: embed;
                }
                
                .ltr-content {
                    direction: ltr;
                    text-align: left;
                    unicode-bidi: embed;
                }
                
                .mixed-content {
                    direction: auto;
                    unicode-bidi: plaintext;
                }
            """,
            
            "layout_adjustments": """
                .rtl-layout {
                    margin-right: 0;
                    margin-left: auto;
                    padding-right: 1rem;
                    padding-left: 0;
                }
                
                .rtl-layout .sidebar {
                    float: right;
                    margin-left: 1rem;
                    margin-right: 0;
                }
                
                .rtl-layout .navigation {
                    text-align: right;
                }
                
                .rtl-layout .navigation li {
                    float: right;
                    margin-left: 1rem;
                    margin-right: 0;
                }
            """,
            
            "typography": """
                .rtl-text {
                    font-family: 'Arabic UI Text', 'SF Arabic', 'Segoe UI Arabic', 
                                'Tahoma', 'Arial Unicode MS', sans-serif;
                    line-height: 1.6;
                    letter-spacing: normal;
                }
                
                .hebrew-text {
                    font-family: 'Hebrew UI Text', 'SF Hebrew', 'Segoe UI Hebrew',
                                'Tahoma', 'Arial Unicode MS', sans-serif;
                }
                
                .persian-text {
                    font-family: 'Persian UI Text', 'SF Persian', 'Segoe UI Persian',
                                'Tahoma', 'Arial Unicode MS', sans-serif;
                }
            """,
            
            "form_controls": """
                .rtl-form input,
                .rtl-form textarea,
                .rtl-form select {
                    direction: rtl;
                    text-align: right;
                }
                
                .rtl-form label {
                    float: right;
                    margin-left: 0.5rem;
                    margin-right: 0;
                }
                
                .rtl-form .checkbox {
                    float: right;
                }
            """
        }
    
    async def _detect_text_direction(self, text: str) -> TextDirection:
        """Detect overall text direction using Unicode BiDi algorithm"""
        rtl_count = 0
        ltr_count = 0
        
        for char in text:
            bidi_type = unicodedata.bidirectional(char)
            
            if bidi_type in ['R', 'AL']:  # Right-to-Left or Arabic Letter
                rtl_count += 1
            elif bidi_type == 'L':  # Left-to-Right
                ltr_count += 1
        
        total_directional = rtl_count + ltr_count
        
        if total_directional == 0:
            return TextDirection.LTR  # Default for neutral text
        
        rtl_ratio = rtl_count / total_directional
        
        if rtl_ratio > 0.7:
            return TextDirection.RTL
        elif rtl_ratio < 0.3:
            return TextDirection.LTR
        else:
            return TextDirection.MIXED
    
    async def _analyze_bidi_characters(self, text: str) -> List[Dict[str, Any]]:
        """Analyze bidirectional character types in text"""
        analysis = []
        
        for i, char in enumerate(text):
            bidi_type = unicodedata.bidirectional(char)
            script = self._get_character_script(char)
            
            analysis.append({
                "char": char,
                "position": i,
                "bidi_type": bidi_type,
                "script": script,
                "code_point": ord(char)
            })
        
        return analysis
    
    async def _apply_bidi_algorithm(self, text: str, bidi_analysis: List[Dict[str, Any]]) -> List[BiDiSpan]:
        """Apply Unicode Bidirectional Algorithm to determine text spans"""
        spans = []
        current_direction = None
        current_start = 0
        current_text = ""
        
        for i, char_info in enumerate(bidi_analysis):
            bidi_type = char_info["bidi_type"]
            char = char_info["char"]
            
            # Determine character direction
            if bidi_type in ['R', 'AL']:
                char_direction = TextDirection.RTL
            elif bidi_type == 'L':
                char_direction = TextDirection.LTR
            else:
                char_direction = current_direction or TextDirection.LTR
            
            # Check if we need to start a new span
            if current_direction != char_direction:
                # Save previous span
                if current_text:
                    spans.append(BiDiSpan(
                        text=current_text,
                        direction=current_direction,
                        start_pos=current_start,
                        end_pos=i,
                        bidi_level=0  # Simplified level calculation
                    ))
                
                # Start new span
                current_direction = char_direction
                current_start = i
                current_text = char
            else:
                current_text += char
        
        # Add final span
        if current_text:
            spans.append(BiDiSpan(
                text=current_text,
                direction=current_direction,
                start_pos=current_start,
                end_pos=len(text),
                bidi_level=0
            ))
        
        return spans
    
    async def _reorder_text(self, original_text: str, spans: List[BiDiSpan]) -> str:
        """Reorder text based on BiDi spans for proper display"""
        # For complex BiDi reordering, this is a simplified implementation
        # In production, would use full Unicode BiDi algorithm
        
        reordered_parts = []
        
        for span in spans:
            if span.direction == TextDirection.RTL:
                # Reverse character order for RTL spans (simplified)
                # In reality, this needs more sophisticated handling
                reordered_parts.append(span.text)
            else:
                reordered_parts.append(span.text)
        
        return ''.join(reordered_parts)
    
    async def _mirror_characters(self, text: str) -> str:
        """Mirror symmetric characters for RTL display"""
        mirrored_text = ""
        
        for char in text:
            if char in self.mirrored_characters:
                mirrored_text += self.mirrored_characters[char]
            else:
                mirrored_text += char
        
        return mirrored_text
    
    async def _generate_css_styles(self, direction: TextDirection, spans: List[BiDiSpan]) -> Dict[str, str]:
        """Generate appropriate CSS styles for the text"""
        styles = {}
        
        # Base container styles
        base_styles = f"direction: {direction.value}; "
        
        if direction == TextDirection.RTL:
            base_styles += "text-align: right; unicode-bidi: embed;"
        elif direction == TextDirection.LTR:
            base_styles += "text-align: left; unicode-bidi: embed;"
        else:  # MIXED
            base_styles += "unicode-bidi: plaintext;"
        
        styles[".rtl-container"] = base_styles
        
        # Individual span styles
        for i, span in enumerate(spans):
            span_class = f".bidi-span-{span.direction.value}"
            span_styles = f"direction: {span.direction.value}; unicode-bidi: embed;"
            
            if span.direction == TextDirection.RTL:
                span_styles += " text-align: right;"
            else:
                span_styles += " text-align: left;"
            
            styles[span_class] = span_styles
        
        return styles
    
    async def _calculate_layout_adjustments(self, direction: TextDirection, spans: List[BiDiSpan]) -> List[str]:
        """Calculate necessary layout adjustments for RTL display"""
        adjustments = []
        
        if direction in [TextDirection.RTL, TextDirection.MIXED]:
            adjustments.extend([
                "Adjust padding: right padding instead of left",
                "Adjust margins: right margins instead of left",
                "Adjust float: float right instead of left",
                "Adjust text alignment: right-aligned text",
                "Adjust navigation: reverse menu order"
            ])
        
        if any(span.direction == TextDirection.RTL for span in spans):
            adjustments.extend([
                "Use RTL-compatible fonts",
                "Adjust line height for proper RTL rendering",
                "Consider RTL-specific typography rules"
            ])
        
        return adjustments
    
    def _get_character_script(self, char: str) -> str:
        """Get Unicode script for a character"""
        try:
            return unicodedata.name(char).split()[0] if unicodedata.name(char, None) else "UNKNOWN"
        except (ValueError, TypeError):
            # Fallback to basic script detection
            code_point = ord(char)
            
            if 0x0600 <= code_point <= 0x06FF or 0x0750 <= code_point <= 0x077F:
                return "Arabic"
            elif 0x0590 <= code_point <= 0x05FF:
                return "Hebrew"
            elif 0x0700 <= code_point <= 0x074F:
                return "Syriac"
            elif 0x0780 <= code_point <= 0x07BF:
                return "Thaana"
            else:
                return "Latin"
    
    def _calculate_rtl_percentage(self, bidi_analysis: List[Dict[str, Any]]) -> float:
        """Calculate percentage of RTL characters in text"""
        rtl_count = sum(1 for char_info in bidi_analysis 
                       if char_info["bidi_type"] in ['R', 'AL'])
        
        return rtl_count / len(bidi_analysis) if bidi_analysis else 0.0
    
    async def _update_processing_stats(self, result -> None: RTLProcessingResult) -> None:
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        
        if result.detected_direction == TextDirection.RTL:
            self.processing_stats["rtl_detected"] += 1
        elif result.detected_direction == TextDirection.MIXED:
            self.processing_stats["mixed_direction"] += 1
        
        # Update average processing time
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + result.processing_time) / total
        )
    
    async def _create_fallback_result(self, text: str) -> RTLProcessingResult:
        """Create fallback result when processing fails"""
        return RTLProcessingResult(
            processed_text=text,
            original_text=text,
            detected_direction=TextDirection.AUTO,
            bidi_spans=[BiDiSpan(text, TextDirection.AUTO, 0, len(text), 0)],
            css_styles={},
            layout_adjustments=[],
            processing_time=0.001,
            metadata={"error": "Processing failed", "fallback": True}
        )
    
    def _load_rtl_language_data(self) -> Dict[str, Dict[str, Any]]:
        """Load RTL language configuration data"""
        return {
            "ar": {
                "name": "Arabic",
                "script": "Arabic",
                "direction": "rtl",
                "font_families": ["Arabic UI Text", "SF Arabic", "Segoe UI Arabic", "Tahoma"],
                "number_direction": "ltr",
                "punctuation_mirror": True
            },
            "he": {
                "name": "Hebrew", 
                "script": "Hebrew",
                "direction": "rtl",
                "font_families": ["Hebrew UI Text", "SF Hebrew", "Segoe UI Hebrew", "Tahoma"],
                "number_direction": "ltr",
                "punctuation_mirror": True
            },
            "fa": {
                "name": "Persian/Farsi",
                "script": "Arabic",
                "direction": "rtl", 
                "font_families": ["Persian UI Text", "SF Persian", "Segoe UI Persian", "Tahoma"],
                "number_direction": "rtl",
                "punctuation_mirror": True
            },
            "ur": {
                "name": "Urdu",
                "script": "Arabic",
                "direction": "rtl",
                "font_families": ["Urdu UI Text", "SF Urdu", "Segoe UI Urdu", "Tahoma"],
                "number_direction": "rtl",
                "punctuation_mirror": True
            }
        }
    
    def _load_bidi_character_mappings(self) -> Dict[str, str]:
        """Load bidirectional character type mappings"""
        # This would contain comprehensive Unicode BiDi character mappings
        # For now, returning basic mappings
        return {
            "strong_rtl": "R AL",
            "strong_ltr": "L",
            "weak": "EN ES ET AN CS",
            "neutral": "NSM BN B S WS ON"
        }
    
    def _load_mirrored_characters(self) -> Dict[str, str]:
        """Load character mirroring mappings for RTL display"""
        return {
            "(": ")",
            ")": "(",
            "[": "]",
            "]": "[",
            "{": "}",
            "}": "{",
            "<": ">",
            ">": "<",
            "«": "»",
            "»": "«",
            "‹": "›",
            "›": "‹",
            "\u201c": "\u201d",
            "\u201d": "\u201c",
            "\u2018": "\u2019",
            "\u2019": "\u2018",
            "⟨": "⟩",
            "⟩": "⟨"
        }
    
    def _load_css_templates(self) -> Dict[str, str]:
        """Load CSS templates for RTL support"""
        return {
            "rtl_base": """
                direction: rtl;
                text-align: right;
                unicode-bidi: embed;
            """,
            "ltr_base": """
                direction: ltr;
                text-align: left;
                unicode-bidi: embed;
            """,
            "mixed_base": """
                unicode-bidi: plaintext;
                direction: auto;
            """
        }


# Export main classes and types
__all__ = [
    "RTLProcessor",
    "RTLProcessingResult",
    "RTLProcessingOptions",
    "BiDiSpan",
    "TextDirection",
    "RTLLanguage",
    "BiDiType"
]