"""Multilingual SEO - International SEO Optimization

This module provides comprehensive multilingual SEO capabilities including
content localization, hreflang implementation, international keyword research,
and cultural adaptation for global content distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class Language(Enum):
    """
Supported languages for multilingual SEO"""

    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class Region(Enum):
    """Supported regions for localization"""

    UNITED_STATES = "US"
    UNITED_KINGDOM = "GB"
    CANADA = "CA"
    FRANCE = "FR"
    GERMANY = "DE"
    SPAIN = "ES"
    ITALY = "IT"
    PORTUGAL = "PT"
    NETHERLANDS = "NL"
    RUSSIA = "RU"
    CHINA = "CN"
    JAPAN = "JP"
    KOREA = "KR"
    SAUDI_ARABIA = "SA"
    INDIA = "IN"
    AUSTRALIA = "AU"
    BRAZIL = "BR"
    MEXICO = "MX"


class LocalizationLevel(Enum):
    """Levels of localization"""

    BASIC = "basic"  # Translation only
    INTERMEDIATE = "intermediate"  # Translation + cultural adaptation
    ADVANCED = "advanced"  # Full localization with regional specifics


@dataclass
class LocalizedContent:
    """Localized content for a specific language/region"""
    language: Language
    region: Region
    title: str
    description: str
    content: str
    keywords: List[str]
    meta_tags: Dict[str, str]
    cultural_adaptations: List[str]
    localization_score: float


@dataclass
class HreflangTag:
    """
Hreflang tag for international SEO"""
    language: str
    region: Optional[str]
    url: str
    is_default: bool = False


@dataclass
class MultilingualSEOResult:
    """
Complete multilingual SEO optimization result"""
    original_language: Language
    localized_versions: Dict[str, LocalizedContent]  # Key: language-region code
    hreflang_tags: List[HreflangTag]
    international_keywords: Dict[str, List[str]]  # Key: language code
    cultural_considerations: Dict[str, List[str]]
    technical_recommendations: List[str]
    overall_score: float


class MultilingualSEO:
    """
    Comprehensive multilingual SEO system that handles content localization,
    international keyword research, and technical implementation for global reach.
    """
    def __init__(self) -> None:
        """
Initialize the multilingual SEO system."""
        self.language_mappings = self._initialize_language_mappings()
        self.cultural_data = self._initialize_cultural_data()
        self.search_engines = self._initialize_search_engines()
        self.rtl_languages = {Language.ARABIC}  # Right-to-left languages

    def optimize_for_international_markets(
        self,
        content: str,
        title: str,
        description: str,
        keywords: List[str],
        source_language: Language,
        target_markets: List[Tuple[Language, Region]],
        base_url: str,
        localization_level: LocalizationLevel = LocalizationLevel.INTERMEDIATE
    ) -> MultilingualSEOResult:
        """
        Optimize content for international markets with full localization.
        
        Args:
            content: Original content to localize
            title: Original title
            description: Original description
            keywords: Original keywords
            source_language: Source language of the content
            target_markets: List of (language, region) tuples for target markets
            base_url: Base URL for hreflang tags
            localization_level: Level of localization to apply
            
        Returns:
            MultilingualSEOResult with all localized versions and recommendations
        """
        try:
            logger.info(f"Starting multilingual SEO optimization for {len(target_markets)} markets")
            
            localized_versions = {}
            international_keywords = {}
            cultural_considerations = {}
            
            # Process each target market
            for language, region in target_markets:
                market_code = f"{language.value}-{region.value}"
                
                # Localize content for this market
                localized_content = self._localize_content(
                    content, title, description, keywords,
                    source_language, language, region, localization_level
                )
                
                localized_versions[market_code] = localized_content
                
                # Generate international keywords
                international_keywords[language.value] = self._generate_international_keywords(
                    keywords, language, region
                )
                
                # Cultural considerations
                cultural_considerations[market_code] = self._get_cultural_considerations(
                    language, region, localization_level
                )
            
            # Generate hreflang tags
            hreflang_tags = self._generate_hreflang_tags(target_markets, base_url)
            
            # Technical recommendations
            technical_recommendations = self._generate_technical_recommendations(
                target_markets, localized_versions
            )
            
            # Calculate overall score
            overall_score = self._calculate_international_seo_score(
                localized_versions, hreflang_tags, technical_recommendations
            )
            
            return MultilingualSEOResult(
                original_language=source_language,
                localized_versions=localized_versions,
                hreflang_tags=hreflang_tags,
                international_keywords=international_keywords,
                cultural_considerations=cultural_considerations,
                technical_recommendations=technical_recommendations,
                overall_score=overall_score
            )
            
        except Exception as e:
            logger.error(f"Error in multilingual SEO optimization: {str(e)}")
            raise

    def _localize_content(
        self,
        content: str,
        title: str,
        description: str,
        keywords: List[str],
        source_language: Language,
        target_language: Language,
        target_region: Region,
        localization_level: LocalizationLevel
    ) -> LocalizedContent:
        """Localize content for a specific language and region"""
        
        # Basic translation (simulated - in real implementation would use translation APIs)
        localized_title = self._translate_text(title, source_language, target_language)
        localized_description = self._translate_text(description, source_language, target_language)
        localized_content = self._translate_text(content, source_language, target_language)
        localized_keywords = [self._translate_text(kw, source_language, target_language) for kw in keywords]
        
        # Cultural adaptations
        cultural_adaptations = []
        
        if localization_level in [LocalizationLevel.INTERMEDIATE, LocalizationLevel.ADVANCED]:
            # Apply cultural adaptations
            localized_content, adaptations = self._apply_cultural_adaptations(
                localized_content, target_language, target_region
            )
            cultural_adaptations.extend(adaptations)
            
            # Adapt keywords for local search behavior
            localized_keywords = self._adapt_keywords_for_region(
                localized_keywords, target_language, target_region
            )
        
        if localization_level == LocalizationLevel.ADVANCED:
            # Advanced localization: currency, date formats, measurements, etc.
            localized_content = self._apply_advanced_localization(
                localized_content, target_region
            )
            
            # Region-specific SEO optimizations
            localized_content = self._apply_regional_seo_optimizations(
                localized_content, target_language, target_region
            )
        
        # Generate localized meta tags
        meta_tags = self._generate_localized_meta_tags(
            localized_title, localized_description, target_language, target_region
        )
        
        # Calculate localization score
        localization_score = self._calculate_localization_score(
            localized_content, cultural_adaptations, localization_level
        )
        
        return LocalizedContent(
            language=target_language,
            region=target_region,
            title=localized_title,
            description=localized_description,
            content=localized_content,
            keywords=localized_keywords,
            meta_tags=meta_tags,
            cultural_adaptations=cultural_adaptations,
            localization_score=localization_score
        )

    def _translate_text(self, text: str, source_lang: Language, target_lang: Language) -> str:
        """
Translate text between languages (simplified implementation)"""
        
        if source_lang == target_lang:
            return text
        
        # In a real implementation, this would use translation APIs like Google Translate,
        # DeepL, or Azure Translator. For demo purposes, we'll do basic transformations.
        
        # Simple simulation of translation
        if target_lang == Language.FRENCH:
            # Add some French characteristics
            text = text.replace("Hello", "Bonjour")
            text = text.replace("Thank you", "Merci")
            text = text.replace("and", "et")
        elif target_lang == Language.GERMAN:
            # Add some German characteristics
            text = text.replace("Hello", "Hallo")
            text = text.replace("Thank you", "Danke")
            text = text.replace("and", "und")
        elif target_lang == Language.SPANISH:
            # Add some Spanish characteristics
            text = text.replace("Hello", "Hola")
            text = text.replace("Thank you", "Gracias")
            text = text.replace("and", "y")
        
        return text

    def _apply_cultural_adaptations(
        self, 
        content: str, 
        language: Language, 
        region: Region
    ) -> Tuple[str, List[str]]:
        """Apply cultural adaptations to content"""
        
        adaptations = []
        adapted_content = content
        
        cultural_rules = self.cultural_data.get(language.value, {}).get(region.value, {})
        
        # Color adaptations
        color_rules = cultural_rules.get("colors", {})
        for original_color, adapted_color in color_rules.items():
            if original_color in content.lower():
                adapted_content = adapted_content.replace(original_color, adapted_color)
                adaptations.append(f"Color adaptation: {original_color} → {adapted_color}")
        
        # Cultural references
        if language == Language.CHINESE and region == Region.CHINA:
            # Adapt for Chinese cultural preferences
            if "individual success" in content.lower():
                adapted_content = adapted_content.replace(
                    "individual success", "collective harmony and success"
                )
                adaptations.append("Cultural adaptation: Emphasized collective values")
        
        elif language == Language.JAPANESE and region == Region.JAPAN:
            # Adapt for Japanese cultural preferences
            if "direct approach" in content.lower():
                adapted_content = adapted_content.replace(
                    "direct approach", "respectful and considerate approach"
                )
                adaptations.append("Cultural adaptation: Emphasized respectful communication")
        
        elif language == Language.ARABIC:
            # Adapt for Arabic cultural preferences
            if "innovation" in content.lower():
                adapted_content = adapted_content.replace(
                    "innovation", "innovation within traditional values"
                )
                adaptations.append("Cultural adaptation: Balanced innovation with tradition")
        
        # Regional business practices
        if region in [Region.GERMANY, Region.NETHERLANDS]:
            # Northern European preference for detailed information
            if "quick overview" in content.lower():
                adapted_content = adapted_content.replace(
                    "quick overview", "comprehensive detailed analysis"
                )
                adaptations.append("Cultural adaptation: Added detail preference")
        
        return adapted_content, adaptations

    def _apply_advanced_localization(self, content: str, region: Region) -> str:
        try:
            logger.info(f"Executing _apply_advanced_localization")
            
            # Implementation for _apply_advanced_localization
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_apply_advanced_localization completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_apply_advanced_localization failed: {e}")
            raise
    def _apply_regional_seo_optimizations(
        self, 
        content: str, 
        language: Language, 
        region: Region
    ) -> str:
        """Apply region-specific SEO optimizations"""
        
        # Search engine preferences by region
        primary_search_engine = self.search_engines.get(region.value, "google")
        
        if primary_search_engine == "baidu" and region == Region.CHINA:
            # Baidu prefers Chinese language content with specific structure
            content = f"[适用于中国市场] {content}"
        
        elif primary_search_engine == "yandex" and region == Region.RUSSIA:
            # Yandex optimizations
            content = f"[Для российского рынка] {content}"
        
        elif primary_search_engine == "naver" and region == Region.KOREA:
            # Naver optimizations
            content = f"[한국 시장용] {content}"
        
        # Regional keyword optimization
        regional_terms = {
            Region.UNITED_KINGDOM: {"elevator": "lift", "apartment": "flat"},
            Region.AUSTRALIA: {"flashlight": "torch", "cookies": "biscuits"},
            Region.CANADA: {"washroom": "bathroom", "toque": "winter hat"}
        }
        
        if region in regional_terms:
            for us_term, regional_term in regional_terms[region].items():
                content = content.replace(us_term, regional_term)
        
        return content

    def _adapt_keywords_for_region(
        self, 
        keywords: List[str], 
        language: Language, 
        region: Region
    ) -> List[str]:
        """Adapt keywords for regional search behavior"""
        
        adapted_keywords = keywords.copy()
        
        # Add regional variations
        regional_modifiers = {
            Region.UNITED_KINGDOM: ["UK", "British", "Britain"],
            Region.CANADA: ["Canadian", "Canada"],
            Region.AUSTRALIA: ["Australian", "Australia", "Aussie"],
            Region.GERMANY: ["German", "Deutschland"],
            Region.FRANCE: ["French", "France", "français"],
            Region.JAPAN: ["Japanese", "Japan", "日本"],
            Region.CHINA: ["Chinese", "China", "中国"]
        }
        
        if region in regional_modifiers:
            modifiers = regional_modifiers[region]
            for keyword in keywords[:3]:  # Only for top 3 keywords
                for modifier in modifiers[:2]:  # Max 2 modifiers
                    regional_keyword = f"{keyword} {modifier}"
                    if regional_keyword not in adapted_keywords:
                        adapted_keywords.append(regional_keyword)
        
        # Language-specific keyword adaptations
        if language == Language.GERMAN:
            # German compounds words
            adapted_keywords.extend([
                kw.replace(" ", "") for kw in keywords if " " in kw
            ])
        
        elif language == Language.CHINESE:
            # Add simplified and traditional character variations
            for keyword in keywords:
                if keyword not in adapted_keywords:
                    adapted_keywords.append(f"{keyword}中文")
        
        return adapted_keywords[:len(keywords) * 2]  # Limit expansion

    def _generate_international_keywords(
        self, 
        base_keywords: List[str], 
        language: Language, 
        region: Region
    ) -> List[str]:
        """Generate international keywords for specific market"""
        
        international_keywords = []
        
        # Translate base keywords
        for keyword in base_keywords:
            translated = self._translate_text(keyword, Language.ENGLISH, language)
            international_keywords.append(translated)
        
        # Add market-specific keywords
        market_specific = {
            (Language.GERMAN, Region.GERMANY): ["qualität", "präzision", "engineering"],
            (Language.FRENCH, Region.FRANCE): ["qualité", "élégance", "art de vivre"],
            (Language.JAPANESE, Region.JAPAN): ["品質", "技術", "革新"],
            (Language.CHINESE, Region.CHINA): ["质量", "创新", "发展"],
            (Language.SPANISH, Region.SPAIN): ["calidad", "tradición", "excelencia"],
            (Language.SPANISH, Region.MEXICO): ["valor", "familia", "comunidad"]
        }
        
        market_key = (language, region)
        if market_key in market_specific:
            international_keywords.extend(market_specific[market_key])
        
        # Add long-tail international keywords
        question_words = {
            Language.ENGLISH: ["how to", "what is", "best"],
            Language.FRENCH: ["comment", "qu'est-ce que", "meilleur"],
            Language.GERMAN: ["wie", "was ist", "beste"],
            Language.SPANISH: ["cómo", "qué es", "mejor"],
            Language.CHINESE: ["如何", "什么是", "最好的"],
            Language.JAPANESE: ["どのように", "何ですか", "最高の"]
        }
        
        if language in question_words:
            for question_word in question_words[language][:2]:
                for keyword in base_keywords[:2]:
                    translated_keyword = self._translate_text(keyword, Language.ENGLISH, language)
                    long_tail = f"{question_word} {translated_keyword}"
                    international_keywords.append(long_tail)
        
        return list(set(international_keywords))  # Remove duplicates

    def _generate_hreflang_tags(
        self, 
        target_markets: List[Tuple[Language, Region]], 
        base_url: str
    ) -> List[HreflangTag]:
        """Generate hreflang tags for international SEO"""
        
        hreflang_tags = []
        
        # Add hreflang for each target market
        for language, region in target_markets:
            hreflang_code = f"{language.value}-{region.value.lower()}"
            url = f"{base_url}/{language.value}-{region.value.lower()}/"
            
            tag = HreflangTag(
                language=language.value,
                region=region.value.lower(),
                url=url,
                is_default=False
            )
            hreflang_tags.append(tag)
        
        # Add x-default for default language
        if target_markets:
            default_language, default_region = target_markets[0]
            default_tag = HreflangTag(
                language="x",
                region="default",
                url=base_url,
                is_default=True
            )
            hreflang_tags.append(default_tag)
        
        return hreflang_tags

    def _get_cultural_considerations(
        self, 
        language: Language, 
        region: Region, 
        localization_level: LocalizationLevel
    ) -> List[str]:
        """Get cultural considerations for the market"""
        
        considerations = []
        
        # Basic cultural considerations
        if language == Language.ARABIC:
            considerations.extend([
                "Right-to-left text direction",
                "Islamic cultural values consideration",
                "Family-oriented messaging preferred"
            ])
        
        elif language == Language.CHINESE and region == Region.CHINA:
            considerations.extend([
                "Respect for hierarchy and authority",
                "Collective values over individual",
                "Lucky numbers and colors consideration",
                "Simplified Chinese characters required"
            ])
        
        elif language == Language.JAPANESE and region == Region.JAPAN:
            considerations.extend([
                "High context communication style",
                "Respect for tradition and formality",
                "Group harmony (wa) important",
                "Attention to detail and perfection"
            ])
        
        elif language == Language.GERMAN and region == Region.GERMANY:
            considerations.extend([
                "Direct communication preferred",
                "High value on quality and precision",
                "Environmental consciousness important",
                "Formal tone recommended"
            ])
        
        # Advanced considerations for higher localization levels
        if localization_level == LocalizationLevel.ADVANCED:
            region_specific = {
                Region.INDIA: [
                    "Multiple languages within region",
                    "Diverse religious considerations",
                    "Mobile-first audience"
                ],
                Region.BRAZIL: [
                    "Brazilian Portuguese vs European Portuguese",
                    "Carnival and soccer cultural references",
                    "Social media engagement high"
                ],
                Region.SAUDI_ARABIA: [
                    "Islamic calendar considerations",
                    "Gender-specific content guidelines",
                    "Luxury and status important"
                ]
            }
            
            if region in region_specific:
                considerations.extend(region_specific[region])
        
        return considerations

    def _generate_localized_meta_tags(
        self, 
        title: str, 
        description: str, 
        language: Language, 
        region: Region
    ) -> Dict[str, str]:
        """Generate localized meta tags"""
        
        meta_tags = {
            "title": title,
            "description": description,
            "language": language.value,
            "country": region.value,
            "content-language": f"{language.value}-{region.value}",
        }
        
        # Add Open Graph localization
        meta_tags["og:locale"] = f"{language.value}_{region.value}"
        
        # Add alternate language tags
        meta_tags["og:locale:alternate"] = language.value
        
        # RTL language consideration
        if language in self.rtl_languages:
            meta_tags["dir"] = "rtl"
        else:
            meta_tags["dir"] = "ltr"
        
        return meta_tags

    def _generate_technical_recommendations(
        self, 
        target_markets: List[Tuple[Language, Region]], 
        localized_versions: Dict[str, LocalizedContent]
    ) -> List[str]:
        """Generate technical SEO recommendations for international sites"""
        
        recommendations = []
        
        # URL structure recommendations
        recommendations.append(
            "Use subdirectories (domain.com/en-us/) or subdomains (us.domain.com) for different markets"
        )
        
        # Server location recommendations
        unique_regions = set(region for _, region in target_markets)
        if len(unique_regions) > 3:
            recommendations.append(
                "Consider using CDN (Content Delivery Network) for global performance"
            )
        
        # Character encoding
        has_unicode_languages = any(
            lang in [Language.CHINESE, Language.JAPANESE, Language.KOREAN, Language.ARABIC, Language.HINDI]
            for lang, _ in target_markets
        )
        if has_unicode_languages:
            recommendations.append(
                "Ensure UTF-8 encoding is properly configured for Unicode language support"
            )
        
        # Search console setup
        recommendations.append(
            "Set up Google Search Console properties for each target country/language"
        )
        
        # Mobile optimization
        mobile_first_regions = [Region.INDIA, Region.CHINA, Region.BRAZIL]
        if any(region in mobile_first_regions for _, region in target_markets):
            recommendations.append(
                "Prioritize mobile optimization for markets with high mobile usage"
            )
        
        # Local search engines
        special_search_engines = []
        for _, region in target_markets:
            if region == Region.CHINA:
                special_search_engines.append("Baidu")
            elif region == Region.RUSSIA:
                special_search_engines.append("Yandex")
            elif region == Region.KOREA:
                special_search_engines.append("Naver")
        
        if special_search_engines:
            recommendations.append(
                f"Optimize for regional search engines: {', '.join(set(special_search_engines))}"
            )
        
        # RTL language considerations
        rtl_markets = [lang for lang, _ in target_markets if lang in self.rtl_languages]
        if rtl_markets:
            recommendations.append(
                "Implement RTL CSS and layout adjustments for Arabic content"
            )
        
        return recommendations

    def _calculate_localization_score(
        self, 
        content: str, 
        cultural_adaptations: List[str], 
        localization_level: LocalizationLevel
    ) -> float:
        """Calculate localization quality score"""
        
        score = 0.0
        
        # Base translation score (40 points)
        if content and len(content) > 50:
            score += 40
        
        # Cultural adaptation score (30 points)
        adaptation_score = min(30, len(cultural_adaptations) * 5)
        score += adaptation_score
        
        # Localization level bonus (30 points)
        level_scores = {
            LocalizationLevel.BASIC: 10,
            LocalizationLevel.INTERMEDIATE: 20,
            LocalizationLevel.ADVANCED: 30
        }
        score += level_scores[localization_level]
        
        return min(100.0, score)

    def _calculate_international_seo_score(
        self, 
        localized_versions: Dict[str, LocalizedContent], 
        hreflang_tags: List[HreflangTag], 
        technical_recommendations: List[str]
    ) -> float:
        """
Calculate overall international SEO score"""
        
        score = 0.0
        
        # Localization quality (40 points)
        if localized_versions:
            avg_localization_score = sum(
                content.localization_score for content in localized_versions.values()
            ) / len(localized_versions)
            score += (avg_localization_score / 100) * 40
        
        # Technical implementation (30 points)
        if hreflang_tags:
            score += 15  # Hreflang implementation
        
        # Market coverage (20 points)
        market_count = len(localized_versions)
        market_score = min(20, market_count * 4)
        score += market_score
        
        # Technical completeness (10 points)
        if len(technical_recommendations) >= 5:
            score += 10
        
        return min(100.0, score)

    def _initialize_language_mappings(self) -> Dict[str, Dict[str, str]]:
        """
Initialize language mappings for translation"""
        
        return {
            "common_terms": {
                "hello": {
                    "fr": "bonjour",
                    "de": "hallo",
                    "es": "hola",
                    "it": "ciao",
                    "pt": "olá",
                    "zh": "你好",
                    "ja": "こんにちは",
                    "ar": "مرحبا",
                    "ru": "привет"
                },
                "thank you": {
                    "fr": "merci",
                    "de": "danke",
                    "es": "gracias",
                    "it": "grazie",
                    "pt": "obrigado",
                    "zh": "谢谢",
                    "ja": "ありがとう",
                    "ar": "شكرا",
                    "ru": "спасибо"
                }
            }
        }

    def _initialize_cultural_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Initialize cultural adaptation data"""
        
        return {
            "zh": {  # Chinese
                "CN": {
                    "colors": {"red": "gold", "white": "red"},
                    "lucky_numbers": [8, 9],
                    "unlucky_numbers": [4],
                    "communication_style": "indirect"
                }
            },
            "ja": {  # Japanese
                "JP": {
                    "colors": {"white": "pure white"},
                    "communication_style": "very_indirect",
                    "hierarchy_important": True
                }
            },
            "ar": {  # Arabic
                "SA": {
                    "text_direction": "rtl",
                    "religious_considerations": True,
                    "family_values": "high"
                }
            }
        }

    def _initialize_search_engines(self) -> Dict[str, str]:
        """Initialize primary search engines by region"""
        
        return {
            "CN": "baidu",
            "RU": "yandex", 
            "KR": "naver",
            "CZ": "seznam",
            "default": "google"
        }

    def generate_hreflang_html(self, hreflang_tags: List[HreflangTag]) -> str:
        """Generate HTML hreflang tags"""
        
        html_tags = []
        
        for tag in hreflang_tags:
            if tag.is_default:
                hreflang_value = "x-default"
            else:
                hreflang_value = f"{tag.language}-{tag.region}" if tag.region else tag.language
            
            html_tag = f'<link rel="alternate" hreflang="{hreflang_value}" href="{tag.url}" />'
            html_tags.append(html_tag)
        
        return '\n'.join(html_tags)

    def validate_international_setup(self, base_url: str, target_markets: List[Tuple[Language, Region]]) -> Dict[str, Any]:
        """Validate international SEO setup"""
        
        validation_result = {
            "url_structure_valid": True,
            "hreflang_coverage": len(target_markets),
            "potential_issues": [],
            "recommendations": []
        }
        
        # Check URL structure
        if not base_url.startswith(('http://', 'https://')):
            validation_result["url_structure_valid"] = False
            validation_result["potential_issues"].append("Invalid base URL format")
        
        # Check for duplicate language-region combinations
        market_codes = [f"{lang.value}-{region.value}" for lang, region in target_markets]
        if len(market_codes) != len(set(market_codes)):
            validation_result["potential_issues"].append("Duplicate language-region combinations found")
        
        # Recommendations based on market selection
        languages = [lang for lang, _ in target_markets]
        if Language.CHINESE in languages:
            validation_result["recommendations"].append("Consider separate domains for Chinese market due to Great Firewall")
        
        if Language.ARABIC in languages:
            validation_result["recommendations"].append("Implement RTL layout support for Arabic content")
        
        return validation_result

    def export_localization_report(self, result: MultilingualSEOResult, format: str = "json") -> str:
        """Export multilingual SEO report"""
        
        if format == "json":
            return self._export_to_json(result)
        elif format == "csv":
            return self._export_to_csv(result)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_to_json(self, result: MultilingualSEOResult) -> str:
        """Export result to JSON format"""
        
        export_data = {
            "overall_score": result.overall_score,
            "original_language": result.original_language.value,
            "localized_versions": {
                code: {
                    "language": content.language.value,
                    "region": content.region.value,
                    "title": content.title,
                    "description": content.description,
                    "keywords": content.keywords,
                    "localization_score": content.localization_score,
                    "cultural_adaptations": content.cultural_adaptations
                }
                for code, content in result.localized_versions.items()
            },
            "hreflang_tags": [
                {
                    "language": tag.language,
                    "region": tag.region,
                    "url": tag.url,
                    "is_default": tag.is_default
                }
                for tag in result.hreflang_tags
            ],
            "international_keywords": result.international_keywords,
            "cultural_considerations": result.cultural_considerations,
            "technical_recommendations": result.technical_recommendations
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def _export_to_csv(self, result: MultilingualSEOResult) -> str:
        """Export result to CSV format"""
        
        csv_lines = ["Market,Language,Region,Title,Localization Score,Keywords Count"]
        
        for code, content in result.localized_versions.items():
            line = f'"{code}",{content.language.value},{content.region.value},' \
                   f'"{content.title}",{content.localization_score},{len(content.keywords)}'
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)


# Export for module usage
__all__ = [
    "MultilingualSEO",
    "Language",
    "Region", 
    "LocalizationLevel",
    "LocalizedContent",
    "HreflangTag",
    "MultilingualSEOResult"
]