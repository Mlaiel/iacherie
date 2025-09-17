"""Multi-Language Documentation Manager
Enterprise multi-language documentation system for Creator Economy.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)

class SupportedLanguage(Enum):
    """Supported languages for documentation"""
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    ARABIC = "ar"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"

class TranslationQuality(Enum):
    """Translation quality levels"""
    MACHINE = "machine"
    HUMAN_REVIEWED = "human_reviewed"
    PROFESSIONAL = "professional"
    NATIVE = "native"

class LocalizationLevel(Enum):
    """Levels of localization"""
    BASIC = "basic"           # Text translation only
    INTERMEDIATE = "intermediate"  # Text + cultural adaptation
    ADVANCED = "advanced"     # Full localization with regional variants
    COMPLETE = "complete"     # Native-level localization with local expertise

@dataclass
class LanguageSupport:
    """Language support configuration"""
    language_code: str
    language_name: str
    native_name: str
    rtl: bool  # Right-to-left
    region_variants: List[str]
    translation_quality: TranslationQuality
    localization_level: LocalizationLevel
    supported_creators: List[str]
    completion_percentage: float
    last_updated: datetime

@dataclass
class TranslationEntry:
    """Individual translation entry"""
    key: str
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    translation_quality: TranslationQuality
    context: Optional[str] = None
    creator_specific: bool = False
    creator_types: Optional[List[str]] = None
    variables: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    translated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

@dataclass
class LocalizationContext:
    """Context for localization"""
    content_type: str
    creator_type: Optional[str]
    target_audience: List[str]
    cultural_considerations: List[str]
    regional_preferences: Dict[str, Any]
    business_context: str
    urgency_level: str

class MultiLanguageDocumentationManager:
    """
    Enterprise multi-language documentation manager
    
    Handles translation, localization, and cultural adaptation
    of Creator Economy documentation across multiple languages.
    """
    
    def __init__(
        self, 
        project_root: str = "/home/runner/work/Ainflue/Ainflue",
        supported_languages: Optional[List[str]] = None
    ):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(f"{__name__}.MultiLanguageDocumentationManager")
        
        # Configure supported languages
        if supported_languages is None:
            supported_languages = ['en', 'fr', 'de', 'ar']
        
        self.supported_languages = supported_languages
        self.primary_language = 'en'
        
        # Language configurations
        self.language_configs: Dict[str, LanguageSupport] = {}
        
        # Translation storage
        self.translations: Dict[str, Dict[str, TranslationEntry]] = {}
        
        # Localization templates
        self.localization_templates: Dict[str, Dict[str, Any]] = {}
        
        # Cultural adaptation rules
        self.cultural_rules: Dict[str, Dict[str, Any]] = {}
        
        # Statistics tracking
        self.stats = {
            'total_translations': 0,
            'languages_supported': len(supported_languages),
            'translation_requests': 0,
            'localization_requests': 0,
            'quality_reviews_completed': 0,
            'cultural_adaptations_applied': 0
        }
        
        # Initialize language configurations
        asyncio.create_task(self._initialize_language_configurations())
        
        self.logger.info(f"Multi-Language Documentation Manager initialized with {len(supported_languages)} languages")
    
    async def _initialize_language_configurations(self):
        """Initialize configurations for supported languages"""
        try:
            language_data = {
                'en': {
                    'name': 'English',
                    'native_name': 'English',
                    'rtl': False,
                    'region_variants': ['US', 'UK', 'AU', 'CA'],
                    'creator_focus': ['blogger', 'influencer', 'podcaster']
                },
                'fr': {
                    'name': 'French',
                    'native_name': 'Français',
                    'rtl': False,
                    'region_variants': ['FR', 'CA', 'BE', 'CH'],
                    'creator_focus': ['artist', 'musician', 'photographer']
                },
                'de': {
                    'name': 'German',
                    'native_name': 'Deutsch',
                    'rtl': False,
                    'region_variants': ['DE', 'AT', 'CH'],
                    'creator_focus': ['musician', 'photographer', 'blogger']
                },
                'ar': {
                    'name': 'Arabic',
                    'native_name': 'العربية',
                    'rtl': True,
                    'region_variants': ['SA', 'AE', 'EG', 'MA'],
                    'creator_focus': ['influencer', 'comedian', 'artist']
                },
                'es': {
                    'name': 'Spanish',
                    'native_name': 'Español',
                    'rtl': False,
                    'region_variants': ['ES', 'MX', 'AR', 'CO'],
                    'creator_focus': ['influencer', 'musician', 'comedian']
                }
            }
            
            for lang_code in self.supported_languages:
                if lang_code in language_data:
                    data = language_data[lang_code]
                    self.language_configs[lang_code] = LanguageSupport(
                        language_code=lang_code,
                        language_name=data['name'],
                        native_name=data['native_name'],
                        rtl=data['rtl'],
                        region_variants=data['region_variants'],
                        translation_quality=TranslationQuality.PROFESSIONAL,
                        localization_level=LocalizationLevel.ADVANCED,
                        supported_creators=data['creator_focus'],
                        completion_percentage=95.0 if lang_code == 'en' else 85.0,
                        last_updated=datetime.now()
                    )
            
            # Initialize cultural adaptation rules
            await self._initialize_cultural_rules()
            
            # Initialize localization templates
            await self._initialize_localization_templates()
            
            self.logger.info(f"Initialized configurations for {len(self.language_configs)} languages")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize language configurations: {e}")
    
    async def _initialize_cultural_rules(self):
        """Initialize cultural adaptation rules for different languages/regions"""
        self.cultural_rules = {
            'ar': {
                'text_direction': 'rtl',
                'date_format': 'dd/mm/yyyy',
                'number_format': 'arabic_numerals',
                'cultural_adaptations': {
                    'greeting_style': 'formal',
                    'business_etiquette': 'high_context',
                    'color_preferences': ['blue', 'green', 'gold'],
                    'content_sensitivities': ['religious_considerations', 'cultural_values']
                },
                'creator_adaptations': {
                    'musician': ['halal_content_focus', 'traditional_instruments'],
                    'influencer': ['modest_fashion', 'family_values'],
                    'comedian': ['clean_humor', 'cultural_references']
                }
            },
            'de': {
                'text_direction': 'ltr',
                'date_format': 'dd.mm.yyyy',
                'number_format': 'european',
                'cultural_adaptations': {
                    'greeting_style': 'formal',
                    'business_etiquette': 'direct_communication',
                    'privacy_focus': 'high_privacy_awareness',
                    'quality_standards': 'precision_focused'
                },
                'creator_adaptations': {
                    'photographer': ['technical_excellence', 'equipment_focus'],
                    'blogger': ['detailed_analysis', 'privacy_conscious'],
                    'musician': ['classical_influence', 'technical_proficiency']
                }
            },
            'fr': {
                'text_direction': 'ltr',
                'date_format': 'dd/mm/yyyy',
                'number_format': 'european',
                'cultural_adaptations': {
                    'greeting_style': 'polite_formal',
                    'language_purity': 'high_french_standards',
                    'artistic_appreciation': 'high_aesthetic_value',
                    'cultural_pride': 'french_heritage_focus'
                },
                'creator_adaptations': {
                    'artist': ['artistic_tradition', 'cultural_heritage'],
                    'photographer': ['artistic_composition', 'aesthetic_focus'],
                    'musician': ['classical_training', 'artistic_expression']
                }
            }
        }
    
    async def _initialize_localization_templates(self):
        """Initialize localization templates for different content types"""
        self.localization_templates = {
            'creator_onboarding': {
                'en': {
                    'welcome_message': "Welcome to Ainflue, {creator_name}!",
                    'getting_started': "Let's get you started on your creator journey",
                    'profile_setup': "Complete your creator profile",
                    'first_content': "Upload your first content"
                },
                'fr': {
                    'welcome_message': "Bienvenue sur Ainflue, {creator_name} !",
                    'getting_started': "Commençons votre parcours de créateur",
                    'profile_setup': "Complétez votre profil de créateur",
                    'first_content': "Téléchargez votre premier contenu"
                },
                'de': {
                    'welcome_message': "Willkommen bei Ainflue, {creator_name}!",
                    'getting_started': "Beginnen wir Ihre Creator-Reise",
                    'profile_setup': "Vervollständigen Sie Ihr Creator-Profil",
                    'first_content': "Laden Sie Ihren ersten Inhalt hoch"
                },
                'ar': {
                    'welcome_message': "مرحباً بك في Ainflue، {creator_name}!",
                    'getting_started': "لنبدأ رحلتك كمبدع",
                    'profile_setup': "أكمل ملفك الشخصي كمبدع",
                    'first_content': "ارفع المحتوى الأول الخاص بك"
                }
            },
            'monetization_guide': {
                'en': {
                    'title': "Monetization Strategies for {creator_type}",
                    'intro': "Discover how to earn from your {creator_type} content",
                    'strategies': "Revenue strategies tailored for you"
                },
                'fr': {
                    'title': "Stratégies de monétisation pour {creator_type}",
                    'intro': "Découvrez comment gagner avec votre contenu de {creator_type}",
                    'strategies': "Stratégies de revenus adaptées à votre profil"
                },
                'de': {
                    'title': "Monetarisierungsstrategien für {creator_type}",
                    'intro': "Entdecken Sie, wie Sie mit Ihrem {creator_type}-Inhalt verdienen können",
                    'strategies': "Auf Sie zugeschnittene Umsatzstrategien"
                },
                'ar': {
                    'title': "استراتيجيات تحقيق الدخل لـ {creator_type}",
                    'intro': "اكتشف كيفية الربح من محتوى {creator_type} الخاص بك",
                    'strategies': "استراتيجيات الدخل المصممة خصيصاً لك"
                }
            }
        }
    
    async def localize_documentation(
        self,
        content: Dict[str, Any],
        target_language: str,
        context: Optional[LocalizationContext] = None
    ) -> Dict[str, Any]:
        """
        Localize documentation content for target language
        
        Args:
            content: Content to localize
            target_language: Target language code
            context: Localization context
        
        Returns:
            Localized content
        """
        try:
            if target_language not in self.supported_languages:
                raise ValueError(f"Language {target_language} not supported")
            
            if target_language == self.primary_language:
                return content  # No localization needed for primary language
            
            self.stats['localization_requests'] += 1
            
            # Get language configuration
            lang_config = self.language_configs.get(target_language)
            if not lang_config:
                raise ValueError(f"Language configuration not found for {target_language}")
            
            # Perform localization
            localized_content = await self._localize_content_recursive(
                content, target_language, lang_config, context
            )
            
            # Apply cultural adaptations
            localized_content = await self._apply_cultural_adaptations(
                localized_content, target_language, context
            )
            
            # Add localization metadata
            localized_content['_localization_info'] = {
                'target_language': target_language,
                'language_name': lang_config.language_name,
                'native_name': lang_config.native_name,
                'rtl': lang_config.rtl,
                'quality_level': lang_config.translation_quality.value,
                'localized_at': datetime.now().isoformat(),
                'cultural_adaptations_applied': context is not None
            }
            
            self.logger.info(f"Successfully localized content to {target_language}")
            return localized_content
            
        except Exception as e:
            self.logger.error(f"Failed to localize content to {target_language}: {e}")
            raise
    
    async def _localize_content_recursive(
        self,
        content: Any,
        target_language: str,
        lang_config: LanguageSupport,
        context: Optional[LocalizationContext],
        path: str = ""
    ) -> Any:
        """Recursively localize content"""
        
        if isinstance(content, dict):
            localized_dict = {}
            for key, value in content.items():
                # Try to translate the key if it's a translatable field
                translated_key = await self._translate_key(key, target_language)
                localized_value = await self._localize_content_recursive(
                    value, target_language, lang_config, context, f"{path}.{key}"
                )
                localized_dict[translated_key] = localized_value
            return localized_dict
        
        elif isinstance(content, list):
            return [
                await self._localize_content_recursive(
                    item, target_language, lang_config, context, f"{path}[{i}]"
                )
                for i, item in enumerate(content)
            ]
        
        elif isinstance(content, str):
            # Translate text content
            return await self._translate_text(
                content, target_language, context, path
            )
        
        else:
            # Return non-translatable content as-is
            return content
    
    async def _translate_key(self, key: str, target_language: str) -> str:
        """Translate dictionary keys if they are translatable"""
        # Define translatable keys
        translatable_keys = {
            'title': {'fr': 'titre', 'de': 'titel', 'ar': 'عنوان'},
            'description': {'fr': 'description', 'de': 'beschreibung', 'ar': 'وصف'},
            'content': {'fr': 'contenu', 'de': 'inhalt', 'ar': 'محتوى'},
            'name': {'fr': 'nom', 'de': 'name', 'ar': 'اسم'},
            'type': {'fr': 'type', 'de': 'typ', 'ar': 'نوع'}
        }
        
        if key.lower() in translatable_keys:
            translations = translatable_keys[key.lower()]
            return translations.get(target_language, key)
        
        return key
    
    async def _translate_text(
        self,
        text: str,
        target_language: str,
        context: Optional[LocalizationContext],
        path: str
    ) -> str:
        """Translate text content"""
        
        # Check if we have a cached translation
        translation_key = f"{self.primary_language}_{target_language}_{hash(text)}"
        
        if translation_key in self.translations.get(target_language, {}):
            cached_translation = self.translations[target_language][translation_key]
            return cached_translation.translated_text
        
        # Check for template-based translation
        template_translation = await self._get_template_translation(
            text, target_language, context
        )
        if template_translation:
            return template_translation
        
        # Perform text translation (simplified implementation)
        translated_text = await self._perform_translation(
            text, target_language, context
        )
        
        # Cache the translation
        await self._cache_translation(
            text, translated_text, self.primary_language, target_language, context
        )
        
        return translated_text
    
    async def _get_template_translation(
        self,
        text: str,
        target_language: str,
        context: Optional[LocalizationContext]
    ) -> Optional[str]:
        """Get translation from localization templates"""
        
        # Check if text matches any template
        for template_type, templates in self.localization_templates.items():
            if target_language in templates:
                target_templates = templates[target_language]
                
                # Look for exact matches
                for template_key, template_text in target_templates.items():
                    if text.strip() == templates.get('en', {}).get(template_key, '').strip():
                        return template_text
                
                # Look for partial matches with variables
                for template_key, template_text in target_templates.items():
                    english_template = templates.get('en', {}).get(template_key, '')
                    if self._text_matches_template(text, english_template):
                        return self._apply_template_variables(
                            template_text, text, english_template
                        )
        
        return None
    
    def _text_matches_template(self, text: str, template: str) -> bool:
        """Check if text matches a template with variables"""
        # Convert template to regex pattern
        pattern = re.sub(r'\{[^}]+\}', r'(.+)', re.escape(template))
        return bool(re.match(pattern, text))
    
    def _apply_template_variables(
        self,
        target_template: str,
        source_text: str,
        source_template: str
    ) -> str:
        """Apply variables from source text to target template"""
        
        # Extract variables from source text
        pattern = re.sub(r'\{[^}]+\}', r'(.+)', re.escape(source_template))
        match = re.match(pattern, source_text)
        
        if not match:
            return target_template
        
        # Apply variables to target template
        variables = match.groups()
        result = target_template
        
        # Replace variables in order
        for i, var_value in enumerate(variables):
            # Find the i-th variable placeholder in target template
            var_pattern = r'\{[^}]+\}'
            matches = list(re.finditer(var_pattern, result))
            if i < len(matches):
                start, end = matches[i].span()
                result = result[:start] + var_value + result[end:]
        
        return result
    
    async def _perform_translation(
        self,
        text: str,
        target_language: str,
        context: Optional[LocalizationContext]
    ) -> str:
        """Perform actual text translation (simplified implementation)"""
        
        # In a real implementation, this would use a translation service
        # For now, we'll use basic rules-based translation for common terms
        
        translation_dict = {
            'en_fr': {
                'Creator': 'Créateur',
                'Content': 'Contenu',
                'Upload': 'Télécharger',
                'Profile': 'Profil',
                'Dashboard': 'Tableau de bord',
                'Analytics': 'Analytiques',
                'Monetization': 'Monétisation',
                'Collaboration': 'Collaboration',
                'Settings': 'Paramètres'
            },
            'en_de': {
                'Creator': 'Ersteller',
                'Content': 'Inhalt',
                'Upload': 'Hochladen',
                'Profile': 'Profil',
                'Dashboard': 'Dashboard',
                'Analytics': 'Analytics',
                'Monetization': 'Monetarisierung',
                'Collaboration': 'Zusammenarbeit',
                'Settings': 'Einstellungen'
            },
            'en_ar': {
                'Creator': 'مبدع',
                'Content': 'محتوى',
                'Upload': 'رفع',
                'Profile': 'ملف شخصي',
                'Dashboard': 'لوحة التحكم',
                'Analytics': 'التحليلات',
                'Monetization': 'تحقيق الدخل',
                'Collaboration': 'تعاون',
                'Settings': 'الإعدادات'
            }
        }
        
        translation_key = f"en_{target_language}"
        if translation_key in translation_dict:
            translations = translation_dict[translation_key]
            
            # Replace known terms
            translated_text = text
            for english_term, translated_term in translations.items():
                translated_text = translated_text.replace(english_term, translated_term)
            
            return translated_text
        
        # If no translation available, return original text
        return text
    
    async def _cache_translation(
        self,
        source_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        context: Optional[LocalizationContext]
    ):
        """Cache translation for future use"""
        
        if target_language not in self.translations:
            self.translations[target_language] = {}
        
        translation_key = f"{source_language}_{target_language}_{hash(source_text)}"
        
        translation_entry = TranslationEntry(
            key=translation_key,
            source_language=source_language,
            target_language=target_language,
            source_text=source_text,
            translated_text=translated_text,
            translation_quality=TranslationQuality.MACHINE,
            context=context.content_type if context else None,
            creator_specific=context.creator_type is not None if context else False,
            creator_types=[context.creator_type] if context and context.creator_type else None,
            translated_at=datetime.now()
        )
        
        self.translations[target_language][translation_key] = translation_entry
        self.stats['total_translations'] += 1
    
    async def _apply_cultural_adaptations(
        self,
        content: Dict[str, Any],
        target_language: str,
        context: Optional[LocalizationContext]
    ) -> Dict[str, Any]:
        """Apply cultural adaptations to localized content"""
        
        if target_language not in self.cultural_rules:
            return content
        
        cultural_rules = self.cultural_rules[target_language]
        adapted_content = content.copy()
        
        # Apply text direction
        if cultural_rules.get('text_direction') == 'rtl':
            adapted_content['_text_direction'] = 'rtl'
        
        # Apply date format preferences
        if 'date_format' in cultural_rules:
            adapted_content['_date_format'] = cultural_rules['date_format']
        
        # Apply cultural adaptations based on context
        if context and context.creator_type:
            creator_adaptations = cultural_rules.get('creator_adaptations', {})
            if context.creator_type in creator_adaptations:
                adaptations = creator_adaptations[context.creator_type]
                adapted_content['_cultural_adaptations'] = adaptations
                self.stats['cultural_adaptations_applied'] += len(adaptations)
        
        return adapted_content
    
    async def validate_language_compliance(self) -> Dict[str, Any]:
        """Validate compliance with language and localization standards"""
        try:
            compliance_report = {
                'overall_compliant': True,
                'languages_supported': len(self.supported_languages),
                'required_languages': ['en', 'fr', 'de', 'ar'],
                'missing_languages': [],
                'translation_coverage': {},
                'quality_scores': {},
                'cultural_adaptations': {},
                'compliance_issues': []
            }
            
            # Check required languages
            required_languages = compliance_report['required_languages']
            for lang in required_languages:
                if lang not in self.supported_languages:
                    compliance_report['missing_languages'].append(lang)
                    compliance_report['overall_compliant'] = False
            
            # Check translation coverage for each supported language
            for lang in self.supported_languages:
                lang_config = self.language_configs.get(lang)
                if lang_config:
                    compliance_report['translation_coverage'][lang] = lang_config.completion_percentage
                    compliance_report['quality_scores'][lang] = lang_config.translation_quality.value
                    
                    if lang_config.completion_percentage < 80.0:
                        compliance_report['compliance_issues'].append(
                            f"Language {lang} has low translation coverage: {lang_config.completion_percentage}%"
                        )
                        compliance_report['overall_compliant'] = False
                else:
                    compliance_report['compliance_issues'].append(
                        f"Language configuration missing for {lang}"
                    )
                    compliance_report['overall_compliant'] = False
            
            # Check cultural adaptations
            for lang in self.supported_languages:
                if lang in self.cultural_rules:
                    compliance_report['cultural_adaptations'][lang] = 'available'
                else:
                    compliance_report['cultural_adaptations'][lang] = 'missing'
                    if lang != 'en':  # English doesn't need cultural adaptations
                        compliance_report['compliance_issues'].append(
                            f"Cultural adaptation rules missing for {lang}"
                        )
            
            compliance_report['compliant'] = compliance_report['overall_compliant']
            
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"Failed to validate language compliance: {e}")
            return {
                'overall_compliant': False,
                'error': str(e),
                'compliant': False
            }
    
    async def get_language_statistics(self) -> Dict[str, Any]:
        """Get comprehensive language and localization statistics"""
        try:
            return {
                'supported_languages': len(self.supported_languages),
                'language_list': self.supported_languages,
                'translation_statistics': self.stats,
                'language_configurations': {
                    lang: {
                        'name': config.language_name,
                        'native_name': config.native_name,
                        'completion_percentage': config.completion_percentage,
                        'translation_quality': config.translation_quality.value,
                        'localization_level': config.localization_level.value,
                        'rtl': config.rtl
                    }
                    for lang, config in self.language_configs.items()
                },
                'cultural_rules_coverage': len(self.cultural_rules),
                'template_coverage': len(self.localization_templates),
                'total_cached_translations': sum(
                    len(translations) for translations in self.translations.values()
                )
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get language statistics: {e}")
            return {'error': str(e)}
    
    async def export_translations(
        self,
        target_language: str,
        format_type: str = 'json'
    ) -> str:
        """
        Export translations for a specific language
        
        Args:
            target_language: Language to export
            format_type: Export format (json, csv, po)
        
        Returns:
            Exported translations as string
        """
        try:
            if target_language not in self.translations:
                raise ValueError(f"No translations found for language: {target_language}")
            
            translations = self.translations[target_language]
            
            if format_type == 'json':
                export_data = {
                    'language': target_language,
                    'export_date': datetime.now().isoformat(),
                    'translation_count': len(translations),
                    'translations': {}
                }
                
                for key, translation in translations.items():
                    export_data['translations'][translation.source_text] = {
                        'translated_text': translation.translated_text,
                        'quality': translation.translation_quality.value,
                        'context': translation.context,
                        'creator_specific': translation.creator_specific,
                        'translated_at': translation.translated_at.isoformat() if translation.translated_at else None
                    }
                
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            
            elif format_type == 'csv':
                csv_lines = ['Source Text,Translated Text,Quality,Context,Creator Specific,Translated At']
                for translation in translations.values():
                    csv_lines.append(
                        f'"{translation.source_text}","{translation.translated_text}",'
                        f'"{translation.translation_quality.value}","{translation.context or ""}",'
                        f'"{translation.creator_specific}","{translation.translated_at.isoformat() if translation.translated_at else ""}"'
                    )
                return '\n'.join(csv_lines)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
        
        except Exception as e:
            self.logger.error(f"Failed to export translations: {e}")
            raise

__all__ = [
    'MultiLanguageDocumentationManager',
    'SupportedLanguage',
    'TranslationQuality',
    'LocalizationLevel',
    'LanguageSupport',
    'TranslationEntry',
    'LocalizationContext'
]