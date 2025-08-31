"""
RTL Language Support Engine - Ainflue Platform
================================================================================
Module: core/i18n/rtl_language_support.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial RTL Support Engine - Right-to-Left Language Processing
Responsibility: Comprehensive RTL text processing, layout adaptation, and bidirectional text support
Technologies: Python, Unicode BiDi Algorithm, CSS RTL, Layout Processing
================================================================================

  PROPRIETARY SOFTWARE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Text analysis → RTL detection → BiDi processing → Layout adaptation → 
CSS generation → Direction handling → Mixed content support → UI transformation
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

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
    UYGHUR = "ug"
    YIDDISH = "yi"


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
    NSM = "NSM"  # Nonspacing Mark
    BN = "BN"    # Boundary Neutral
    B = "B"      # Paragraph Separator
    S = "S"      # Segment Separator
    WS = "WS"    # Whitespace
    ON = "ON"    # Other Neutrals


class LayoutComponent(Enum):
    """UI layout components that need RTL adaptation"""
    TEXT = "text"
    BUTTON = "button"
    INPUT = "input"
    MENU = "menu"
    NAVIGATION = "navigation"
    SIDEBAR = "sidebar"
    MODAL = "modal"
    CARD = "card"
    LIST = "list"
    TABLE = "table"
    FORM = "form"
    HEADER = "header"
    FOOTER = "footer"


@dataclass
class BiDiAnalysis:
    """Bidirectional text analysis result"""
    text: str
    overall_direction: TextDirection
    character_types: List[BiDiType]
    directional_runs: List[Tuple[int, int, TextDirection]]
    requires_bidi_processing: bool
    neutral_characters: List[int]
    embedding_levels: List[int]
    visual_order: List[int]
    logical_order: List[int]


@dataclass
class RTLAdaptation:
    """RTL adaptation instructions"""
    direction: TextDirection
    css_properties: Dict[str, str]
    layout_adjustments: Dict[str, Any]
    text_alignment: str
    margin_adjustments: Dict[str, str]
    padding_adjustments: Dict[str, str]
    icon_mirroring: bool
    scroll_direction: str
    reading_order: List[str]
    component_adaptations: Dict[LayoutComponent, Dict[str, Any]]


@dataclass
class RTLProcessor:
    """RTL processing configuration"""
    language: RTLLanguage
    script_direction: TextDirection
    number_format: str
    date_format: str
    calendar_type: str
    sorting_rules: List[str]
    punctuation_handling: str
    mixed_content_strategy: str


class RTLLanguageSupport:
    """Advanced RTL language support and processing engine"""
    
    def __init__(self):
        self.rtl_languages: Dict[str, RTLProcessor] = {}
        self.bidi_cache: Dict[str, BiDiAnalysis] = {}
        self.adaptation_cache: Dict[str, RTLAdaptation] = {}
        self.unicode_ranges: Dict[str, Tuple[int, int]] = {}
        
        # Initialize RTL support data
        self._initialize_rtl_languages()
        self._initialize_unicode_ranges()
        self._setup_bidi_algorithm()
        
        logger.info("RTL Language Support Engine initialized")
    
    def _initialize_rtl_languages(self):
        """Initialize RTL language configurations"""
        
        # Arabic
        self.rtl_languages["ar"] = RTLProcessor(
            language=RTLLanguage.ARABIC,
            script_direction=TextDirection.RTL,
            number_format="arabic",
            date_format="hijri",
            calendar_type="islamic",
            sorting_rules=["arabic_collation", "ignore_diacritics"],
            punctuation_handling="contextual",
            mixed_content_strategy="neutral_follows_preceding"
        )
        
        # Hebrew
        self.rtl_languages["he"] = RTLProcessor(
            language=RTLLanguage.HEBREW,
            script_direction=TextDirection.RTL,
            number_format="european",
            date_format="gregorian",
            calendar_type="gregorian",
            sorting_rules=["hebrew_collation", "ignore_points"],
            punctuation_handling="standard",
            mixed_content_strategy="neutral_follows_preceding"
        )
        
        # Persian/Farsi
        self.rtl_languages["fa"] = RTLProcessor(
            language=RTLLanguage.PERSIAN,
            script_direction=TextDirection.RTL,
            number_format="persian",
            date_format="persian",
            calendar_type="solar_hijri",
            sorting_rules=["persian_collation"],
            punctuation_handling="persian_style",
            mixed_content_strategy="neutral_follows_preceding"
        )
        
        # Urdu
        self.rtl_languages["ur"] = RTLProcessor(
            language=RTLLanguage.URDU,
            script_direction=TextDirection.RTL,
            number_format="urdu",
            date_format="islamic",
            calendar_type="islamic",
            sorting_rules=["urdu_collation"],
            punctuation_handling="arabic_style",
            mixed_content_strategy="neutral_follows_preceding"
        )
        
        # Kurdish
        self.rtl_languages["ku"] = RTLProcessor(
            language=RTLLanguage.KURDISH,
            script_direction=TextDirection.RTL,
            number_format="kurdish",
            date_format="kurdish",
            calendar_type="gregorian",
            sorting_rules=["kurdish_collation"],
            punctuation_handling="arabic_style",
            mixed_content_strategy="neutral_follows_preceding"
        )
        
        logger.info(f"Initialized {len(self.rtl_languages)} RTL language processors")
    
    def _initialize_unicode_ranges(self):
        """Initialize Unicode ranges for RTL scripts"""
        self.unicode_ranges = {
            # Arabic script ranges
            "arabic_main": (0x0600, 0x06FF),
            "arabic_supplement": (0x0750, 0x077F),
            "arabic_extended_a": (0x08A0, 0x08FF),
            "arabic_presentation_a": (0xFB50, 0xFDFF),
            "arabic_presentation_b": (0xFE70, 0xFEFF),
            
            # Hebrew script
            "hebrew": (0x0590, 0x05FF),
            "hebrew_presentation": (0xFB1D, 0xFB4F),
            
            # Other RTL scripts
            "syriac": (0x0700, 0x074F),
            "thaana": (0x0780, 0x07BF),
            "nko": (0x07C0, 0x07FF),
            "samaritan": (0x0800, 0x083F),
            "mandaic": (0x0840, 0x085F),
        }
    
    def _setup_bidi_algorithm(self):
        """Setup Unicode Bidirectional Algorithm components"""
        # Character type mappings (simplified)
        self.char_types = {
            # Strong types
            **{chr(i): BiDiType.L for i in range(0x41, 0x5B)},  # A-Z
            **{chr(i): BiDiType.L for i in range(0x61, 0x7B)},  # a-z
            **{chr(i): BiDiType.R for i in range(0x0590, 0x05FF)},  # Hebrew
            **{chr(i): BiDiType.AL for i in range(0x0600, 0x06FF)},  # Arabic
            
            # Numbers
            **{chr(i): BiDiType.EN for i in range(0x30, 0x3A)},  # 0-9
            **{chr(i): BiDiType.AN for i in range(0x0660, 0x066A)},  # Arabic-Indic digits
            
            # Common neutrals
            ' ': BiDiType.WS,
            '\t': BiDiType.WS,
            '\n': BiDiType.B,
            '\r': BiDiType.B,
            '.': BiDiType.CS,
            ',': BiDiType.CS,
            ':': BiDiType.CS,
            ';': BiDiType.CS,
            '!': BiDiType.ON,
            '?': BiDiType.ON,
            '(': BiDiType.ON,
            ')': BiDiType.ON,
            '[': BiDiType.ON,
            ']': BiDiType.ON,
            '{': BiDiType.ON,
            '}': BiDiType.ON,
        }
    
    async def detect_text_direction(self, text: str) -> TextDirection:
        """Detect overall text direction"""



        try:
            if not text.strip():
                return TextDirection.LTR
            
            rtl_count = 0
            ltr_count = 0
            total_chars = 0
            
            for char in text:
                if char.isalpha():
                    total_chars += 1
                    
                    # Check if character is in RTL range
                    if self._is_rtl_character(char):
                        rtl_count += 1
                    else:
                        ltr_count += 1
            
            if total_chars == 0:
                return TextDirection.LTR
            
            rtl_ratio = rtl_count / total_chars
            
            if rtl_ratio > 0.7:
                return TextDirection.RTL
            elif rtl_ratio > 0.3:
                return TextDirection.MIXED
            else:
                return TextDirection.LTR
                
        except Exception as e:
            logger.error(f"Error detecting text direction: {e}")
            return TextDirection.LTR
    
    def _is_rtl_character(self, char: str) -> bool:
        """Check if character is RTL"""
        char_code = ord(char)
        
        # Check all RTL Unicode ranges
        for range_name, (start, end) in self.unicode_ranges.items():
            if start <= char_code <= end:
                return True
        
        return False
    
    async def analyze_bidi_text(self, text: str) -> BiDiAnalysis:
        """Perform bidirectional text analysis"""



        try:
            # Check cache
            if text in self.bidi_cache:
                return self.bidi_cache[text]
            
            # Analyze character types
            char_types = []
            for char in text:
                char_type = self.char_types.get(char, BiDiType.ON)
                char_types.append(char_type)
            
            # Detect overall direction
            overall_direction = await self.detect_text_direction(text)
            
            # Find directional runs
            directional_runs = self._find_directional_runs(char_types)
            
            # Check if BiDi processing is required
            requires_bidi = self._requires_bidi_processing(char_types, overall_direction)
            
            # Find neutral characters
            neutral_chars = [i for i, ct in enumerate(char_types) if ct in [BiDiType.WS, BiDiType.ON]]
            
            # Calculate embedding levels (simplified)
            embedding_levels = self._calculate_embedding_levels(char_types, overall_direction)
            
            # Calculate visual order (simplified)
            visual_order, logical_order = self._calculate_visual_order(text, embedding_levels)
            
            analysis = BiDiAnalysis(
                text=text,
                overall_direction=overall_direction,
                character_types=char_types,
                directional_runs=directional_runs,
                requires_bidi_processing=requires_bidi,
                neutral_characters=neutral_chars,
                embedding_levels=embedding_levels,
                visual_order=visual_order,
                logical_order=logical_order
            )
            
            # Cache result
            self.bidi_cache[text] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing BiDi text: {e}")
            return BiDiAnalysis(
                text=text,
                overall_direction=TextDirection.LTR,
                character_types=[],
                directional_runs=[],
                requires_bidi_processing=False,
                neutral_characters=[],
                embedding_levels=[],
                visual_order=[],
                logical_order=[]
            )
    
    def _find_directional_runs(self, char_types: List[BiDiType]) -> List[Tuple[int, int, TextDirection]]:
        """Find sequences of characters with the same directionality"""
        runs = []
        current_direction = None
        run_start = 0
        
        for i, char_type in enumerate(char_types):
            if char_type in [BiDiType.L]:
                direction = TextDirection.LTR
            elif char_type in [BiDiType.R, BiDiType.AL]:
                direction = TextDirection.RTL
            else:
                continue  # Skip neutral characters for run detection
            
            if current_direction != direction:
                if current_direction is not None:
                    runs.append((run_start, i - 1, current_direction))
                current_direction = direction
                run_start = i
        
        # Add final run
        if current_direction is not None:
            runs.append((run_start, len(char_types) - 1, current_direction))
        
        return runs
    
    def _requires_bidi_processing(self, char_types: List[BiDiType], overall_direction: TextDirection) -> bool:
        """Check if text requires bidirectional processing"""
        if overall_direction == TextDirection.MIXED:
            return True
        
        # Check for mixed strong directional characters
        has_ltr = any(ct == BiDiType.L for ct in char_types)
        has_rtl = any(ct in [BiDiType.R, BiDiType.AL] for ct in char_types)
        
        return has_ltr and has_rtl
    
    def _calculate_embedding_levels(self, char_types: List[BiDiType], overall_direction: TextDirection) -> List[int]:
        """Calculate embedding levels for characters (simplified algorithm)"""
        base_level = 1 if overall_direction == TextDirection.RTL else 0
        levels = []
        
        current_level = base_level
        
        for char_type in char_types:
            if char_type in [BiDiType.R, BiDiType.AL]:
                # RTL character - odd level
                if current_level % 2 == 0:
                    current_level += 1
            elif char_type == BiDiType.L:
                # LTR character - even level
                if current_level % 2 == 1:
                    current_level += 1
            # For neutral characters, inherit current level
            
            levels.append(current_level)
        
        return levels
    
    def _calculate_visual_order(self, text: str, embedding_levels: List[int]) -> Tuple[List[int], List[int]]:
        """Calculate visual and logical order (simplified)"""
        logical_order = list(range(len(text)))
        visual_order = list(range(len(text)))
        
        # Group by embedding levels and reverse RTL runs
        for level in set(embedding_levels):
            if level % 2 == 1:  # RTL level
                # Find runs at this level and reverse them
                run_start = None
                for i, char_level in enumerate(embedding_levels):
                    if char_level == level:
                        if run_start is None:
                            run_start = i
                    else:
                        if run_start is not None:
                            # Reverse the run
                            visual_order[run_start:i] = reversed(visual_order[run_start:i])
                            run_start = None
                
                # Handle final run
                if run_start is not None:
                    visual_order[run_start:] = reversed(visual_order[run_start:])
        
        return visual_order, logical_order
    
    async def create_rtl_adaptation(
        self,
        language_code: str,
        content_type: LayoutComponent = LayoutComponent.TEXT,
        custom_requirements: Dict[str, Any] = None
    ) -> RTLAdaptation:
        """Create RTL adaptation instructions"""



        try:
            # Get language processor
            processor = self.rtl_languages.get(language_code)
            if not processor:
                # Default RTL adaptation
                direction = TextDirection.RTL
            else:
                direction = processor.script_direction
            
            # Base CSS properties for RTL
            css_properties = {
                "direction": direction.value,
                "text-align": "right" if direction == TextDirection.RTL else "left",
                "unicode-bidi": "bidi-override" if direction == TextDirection.RTL else "normal"
            }
            
            # Layout adjustments
            layout_adjustments = {
                "flex_direction": "row-reverse" if direction == TextDirection.RTL else "row",
                "text_direction": direction.value,
                "reading_order": "rtl" if direction == TextDirection.RTL else "ltr"
            }
            
            # Margin and padding adjustments
            margin_adjustments = {}
            padding_adjustments = {}
            
            if direction == TextDirection.RTL:
                margin_adjustments = {
                    "margin-left": "margin-right",
                    "margin-right": "margin-left"
                }
                padding_adjustments = {
                    "padding-left": "padding-right",
                    "padding-right": "padding-left"
                }
            
            # Component-specific adaptations
            component_adaptations = self._create_component_adaptations(content_type, direction)
            
            adaptation = RTLAdaptation(
                direction=direction,
                css_properties=css_properties,
                layout_adjustments=layout_adjustments,
                text_alignment="right" if direction == TextDirection.RTL else "left",
                margin_adjustments=margin_adjustments,
                padding_adjustments=padding_adjustments,
                icon_mirroring=direction == TextDirection.RTL,
                scroll_direction="rtl" if direction == TextDirection.RTL else "ltr",
                reading_order=["right-to-left"] if direction == TextDirection.RTL else ["left-to-right"],
                component_adaptations=component_adaptations
            )
            
            # Apply custom requirements
            if custom_requirements:
                self._apply_custom_requirements(adaptation, custom_requirements)
            
            return adaptation
            
        except Exception as e:
            logger.error(f"Error creating RTL adaptation: {e}")
            return RTLAdaptation(
                direction=TextDirection.LTR,
                css_properties={},
                layout_adjustments={},
                text_alignment="left",
                margin_adjustments={},
                padding_adjustments={},
                icon_mirroring=False,
                scroll_direction="ltr",
                reading_order=["left-to-right"],
                component_adaptations={}
            )
    
    def _create_component_adaptations(self, component_type: LayoutComponent, direction: TextDirection) -> Dict[LayoutComponent, Dict[str, Any]]:
        """Create component-specific adaptations"""
        adaptations = {}
        
        if direction == TextDirection.RTL:
            if component_type == LayoutComponent.NAVIGATION:
                adaptations[component_type] = {
                    "menu_alignment": "right",
                    "submenu_direction": "left",
                    "icon_position": "right",
                    "breadcrumb_separator": "←"
                }
            
            elif component_type == LayoutComponent.FORM:
                adaptations[component_type] = {
                    "label_position": "right",
                    "input_alignment": "right",
                    "button_alignment": "left",
                    "validation_message_position": "right"
                }
            
            elif component_type == LayoutComponent.TABLE:
                adaptations[component_type] = {
                    "column_order": "reversed",
                    "sort_indicators": "mirrored",
                    "action_column": "leftmost",
                    "scroll_direction": "rtl"
                }
            
            elif component_type == LayoutComponent.MODAL:
                adaptations[component_type] = {
                    "close_button_position": "left",
                    "action_buttons_order": "reversed",
                    "content_alignment": "right"
                }
            
            elif component_type == LayoutComponent.SIDEBAR:
                adaptations[component_type] = {
                    "position": "right",
                    "collapse_direction": "left",
                    "menu_icons": "right_aligned"
                }
        
        return adaptations
    
    def _apply_custom_requirements(self, adaptation: RTLAdaptation, requirements: Dict[str, Any]):
        """Apply custom requirements to adaptation"""
        if "force_direction" in requirements:
            adaptation.direction = TextDirection(requirements["force_direction"])
        
        if "custom_css" in requirements:
            adaptation.css_properties.update(requirements["custom_css"])
        
        if "disable_icon_mirroring" in requirements:
            adaptation.icon_mirroring = not requirements["disable_icon_mirroring"]
        
        if "custom_alignment" in requirements:
            adaptation.text_alignment = requirements["custom_alignment"]
    
    async def process_mixed_content(
        self,
        text: str,
        base_direction: TextDirection = TextDirection.AUTO
    ) -> Dict[str, Any]:
        """Process text with mixed LTR/RTL content"""



        try:
            # Analyze the text
            analysis = await self.analyze_bidi_text(text)
            
            # If auto-detection requested, use detected direction
            if base_direction == TextDirection.AUTO:
                base_direction = analysis.overall_direction
            
            # Process directional runs
            processed_runs = []
            for start, end, direction in analysis.directional_runs:
                run_text = text[start:end+1]
                processed_runs.append({
                    "text": run_text,
                    "start": start,
                    "end": end,
                    "direction": direction.value,
                    "requires_markup": direction != base_direction
                })
            
            # Generate HTML with directional markup
            html_markup = self._generate_bidi_html(text, processed_runs, base_direction)
            
            # Generate CSS for mixed content
            css_rules = self._generate_mixed_content_css(analysis, base_direction)
            
            return {
                "original_text": text,
                "base_direction": base_direction.value,
                "analysis": analysis,
                "processed_runs": processed_runs,
                "html_markup": html_markup,
                "css_rules": css_rules,
                "requires_bidi_processing": analysis.requires_bidi_processing
            }
            
        except Exception as e:
            logger.error(f"Error processing mixed content: {e}")
            return {
                "original_text": text,
                "error": str(e),
                "requires_bidi_processing": False
            }
    
    def _generate_bidi_html(self, text: str, runs: List[Dict[str, Any]], base_direction: TextDirection) -> str:
        """Generate HTML with proper BiDi markup"""
        html_parts = []
        last_end = 0
        
        for run in runs:
            # Add text before this run
            if run["start"] > last_end:
                html_parts.append(text[last_end:run["start"]])
            
            # Add the run with appropriate markup
            if run["requires_markup"]:
                direction = run["direction"]
                html_parts.append(f'<span dir="{direction}">{run["text"]}</span>')
            else:
                html_parts.append(run["text"])
            
            last_end = run["end"] + 1
        
        # Add remaining text
        if last_end < len(text):
            html_parts.append(text[last_end:])
        
        # Wrap in container with base direction
        html = ''.join(html_parts)
        return f'<div dir="{base_direction.value}">{html}</div>'
    
    def _generate_mixed_content_css(self, analysis: BiDiAnalysis, base_direction: TextDirection) -> List[str]:
        """Generate CSS rules for mixed content"""
        css_rules = [
            f".bidi-container {{ direction: {base_direction.value}; unicode-bidi: embed; }}",
            ".bidi-rtl { direction: rtl; unicode-bidi: bidi-override; }",
            ".bidi-ltr { direction: ltr; unicode-bidi: bidi-override; }",
            ".bidi-neutral { unicode-bidi: normal; }"
        ]
        
        if analysis.requires_bidi_processing:
            css_rules.extend([
                ".bidi-container * { unicode-bidi: inherit; }",
                ".bidi-number { unicode-bidi: embed; direction: ltr; }",
                ".bidi-punctuation { unicode-bidi: normal; }"
            ])
        
        return css_rules
    
    async def adapt_ui_layout(
        self,
        layout_config: Dict[str, Any],
        target_language: str,
        components: List[LayoutComponent] = None
    ) -> Dict[str, Any]:
        """Adapt UI layout for RTL language"""



        try:
            # Check if language requires RTL
            if target_language not in self.rtl_languages:
                return layout_config  # No adaptation needed
            
            adapted_config = layout_config.copy()
            processor = self.rtl_languages[target_language]
            
            # Apply global RTL adaptations
            adapted_config["direction"] = processor.script_direction.value
            adapted_config["text_align"] = "right"
            
            # Adapt specific components
            if components:
                for component in components:
                    adaptation = await self.create_rtl_adaptation(target_language, component)
                    
                    # Apply component-specific adaptations
                    if component in adaptation.component_adaptations:
                        component_config = adaptation.component_adaptations[component]
                        component_key = component.value
                        
                        if component_key not in adapted_config:
                            adapted_config[component_key] = {}
                        
                        adapted_config[component_key].update(component_config)
            
            # Add RTL-specific CSS classes
            adapted_config["css_classes"] = adapted_config.get("css_classes", [])
            adapted_config["css_classes"].extend(["rtl-layout", f"rtl-{target_language}"])
            
            return adapted_config
            
        except Exception as e:
            logger.error(f"Error adapting UI layout for RTL: {e}")
            return layout_config
    
    async def get_rtl_metrics(self) -> Dict[str, Any]:
        """Get RTL processing metrics"""



        return {
            "supported_languages": list(self.rtl_languages.keys()),
            "cache_size": len(self.bidi_cache),
            "unicode_ranges": len(self.unicode_ranges),
            "processed_texts": len(self.bidi_cache),
            "rtl_languages_count": len([lang for lang in self.rtl_languages.values() 
                                      if lang.script_direction == TextDirection.RTL])
        }
    
    async def validate_rtl_text(self, text: str, language_code: str) -> Dict[str, Any]:
        """Validate RTL text for correctness"""



        try:
            analysis = await self.analyze_bidi_text(text)
            
            validation_result = {
                "is_valid": True,
                "issues": [],
                "recommendations": []
            }
            
            # Check for common RTL issues
            if analysis.overall_direction == TextDirection.MIXED:
                if not analysis.requires_bidi_processing:
                    validation_result["issues"].append("mixed_content_no_bidi")
                    validation_result["recommendations"].append("add_bidi_markup")
            
            # Check for incorrect neutral character handling
            if analysis.neutral_characters and analysis.requires_bidi_processing:
                validation_result["recommendations"].append("review_neutral_characters")
            
            # Check embedding levels
            max_level = max(analysis.embedding_levels) if analysis.embedding_levels else 0
            if max_level > 5:  # Unusual nesting
                validation_result["issues"].append("excessive_nesting")
                validation_result["recommendations"].append("simplify_text_structure")
            
            validation_result["is_valid"] = len(validation_result["issues"]) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating RTL text: {e}")
            return {
                "is_valid": False,
                "issues": ["validation_error"],
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Health check for RTL language support"""



        try:
            # Check if RTL languages are loaded
            if not self.rtl_languages:
                return False
            
            # Test basic direction detection
            rtl_text = "مرحبا بكم"  # Arabic
            direction = await self.detect_text_direction(rtl_text)
            
            if direction != TextDirection.RTL:
                return False
            
            # Test BiDi analysis
            analysis = await self.analyze_bidi_text("Hello مرحبا World")
            
            return analysis.requires_bidi_processing
            
        except Exception as e:
            logger.error(f"RTL language support health check failed: {e}")
            return False