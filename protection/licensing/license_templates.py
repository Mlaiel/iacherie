"""
 License Template Engine - Professional License Generation System
================================================================

Professional license template management and generation system:
- Dynamic template generation
- Multi-language support
- Legal compliance integration
- Customizable clause libraries
- Industry-standard templates

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Legal Template Specialist + Content Manager + Localization Expert
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    """License template categories"""
    MUSIC_LICENSING = "music_licensing"
    SYNC_LICENSING = "sync_licensing"
    DISTRIBUTION = "distribution"
    PUBLISHING = "publishing"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    MASTER_USE = "master_use"
    CREATIVE_COMMONS = "creative_commons"

class ClauseType(Enum):
    """Legal clause types"""
    GRANT_OF_RIGHTS = "grant_of_rights"
    TERRITORY = "territory"
    DURATION = "duration"
    REVENUE_SHARING = "revenue_sharing"
    TERMINATION = "termination"
    WARRANTIES = "warranties"
    INDEMNIFICATION = "indemnification"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    MORAL_RIGHTS = "moral_rights"

class LanguageCode(Enum):
    """Supported languages"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE = "zh"

@dataclass
class ClauseTemplate:
    """Individual clause template"""
    clause_id: str
    clause_type: ClauseType
    title: str
    template_text: str
    required_variables: List[str]
    optional_variables: List[str]
    jurisdiction_specific: bool
    language: LanguageCode
    version: str
    last_updated: datetime

@dataclass
class LicenseTemplate:
    """Complete license template"""
    template_id: str
    category: TemplateCategory
    name: str
    description: str
    target_jurisdictions: List[str]
    required_clauses: List[ClauseType]
    optional_clauses: List[ClauseType]
    template_structure: Dict[str, Any]
    supported_languages: List[LanguageCode]
    compliance_level: str
    industry_standard: bool
    created_at: datetime
    last_modified: datetime

class LicenseTemplateEngine:
    """
     Professional license template generation engine
    
    Advanced system for generating legally compliant license templates
    with multi-language support and dynamic customization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize license template engine with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Template storage
        self.license_templates = {}
        self.clause_templates = {}
        self.template_variables = {}
        
        # Jinja2 environment for dynamic generation
        template_path = Path(config.get('template_path', 'templates/licenses'))
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Language support
        self.translations = {}
        self.supported_languages = [LanguageCode.ENGLISH, LanguageCode.GERMAN, LanguageCode.FRENCH]
        
        # Performance metrics
        self.metrics = {
            'templates_generated': 0,
            'clauses_rendered': 0,
            'languages_supported': len(self.supported_languages),
            'custom_templates_created': 0
        }
        
        self._load_license_templates()
        self._load_clause_templates()
        self._load_translations()
        self._register_custom_filters()
    
    def _load_license_templates(self):
        """Load comprehensive license templates."""
        templates_data = {
            'standard_music_license': LicenseTemplate(
                template_id='standard_music_license',
                category=TemplateCategory.MUSIC_LICENSING,
                name='Standard Music Licensing Agreement',
                description='Comprehensive music licensing agreement for commercial use',
                target_jurisdictions=['international', 'us', 'eu', 'germany'],
                required_clauses=[
                    ClauseType.GRANT_OF_RIGHTS,
                    ClauseType.TERRITORY,
                    ClauseType.DURATION,
                    ClauseType.REVENUE_SHARING,
                    ClauseType.TERMINATION
                ],
                optional_clauses=[
                    ClauseType.WARRANTIES,
                    ClauseType.INDEMNIFICATION,
                    ClauseType.GOVERNING_LAW,
                    ClauseType.MORAL_RIGHTS
                ],
                template_structure={
                    'sections': [
                        'preamble',
                        'definitions',
                        'grant_of_rights',
                        'territory_and_duration',
                        'financial_terms',
                        'obligations',
                        'termination',
                        'general_provisions',
                        'signatures'
                    ]
                },
                supported_languages=[LanguageCode.ENGLISH, LanguageCode.GERMAN, LanguageCode.FRENCH],
                compliance_level='enterprise',
                industry_standard=True,
                created_at=datetime.now(),
                last_modified=datetime.now()
            ),
            
            'sync_licensing_agreement': LicenseTemplate(
                template_id='sync_licensing_agreement',
                category=TemplateCategory.SYNC_LICENSING,
                name='Synchronization Licensing Agreement',
                description='Agreement for audio-visual synchronization rights',
                target_jurisdictions=['international', 'us', 'eu'],
                required_clauses=[
                    ClauseType.GRANT_OF_RIGHTS,
                    ClauseType.TERRITORY,
                    ClauseType.DURATION,
                    ClauseType.REVENUE_SHARING
                ],
                optional_clauses=[
                    ClauseType.WARRANTIES,
                    ClauseType.MORAL_RIGHTS
                ],
                template_structure={
                    'sections': [
                        'preamble',
                        'work_identification',
                        'synchronization_rights',
                        'usage_limitations',
                        'financial_terms',
                        'delivery_requirements',
                        'signatures'
                    ]
                },
                supported_languages=[LanguageCode.ENGLISH, LanguageCode.FRENCH],
                compliance_level='standard',
                industry_standard=True,
                created_at=datetime.now(),
                last_modified=datetime.now()
            ),
            
            'creative_commons_license': LicenseTemplate(
                template_id='creative_commons_license',
                category=TemplateCategory.CREATIVE_COMMONS,
                name='Creative Commons License',
                description='Open content license with attribution requirements',
                target_jurisdictions=['international'],
                required_clauses=[
                    ClauseType.GRANT_OF_RIGHTS,
                    ClauseType.TERRITORY
                ],
                optional_clauses=[],
                template_structure={
                    'sections': [
                        'license_grant',
                        'attribution_requirements',
                        'restrictions',
                        'disclaimer'
                    ]
                },
                supported_languages=[
                    LanguageCode.ENGLISH, LanguageCode.GERMAN, LanguageCode.FRENCH,
                    LanguageCode.SPANISH, LanguageCode.ITALIAN
                ],
                compliance_level='basic',
                industry_standard=True,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
        }
        
        self.license_templates = templates_data
        self.logger.info(f"Loaded {len(templates_data)} license templates")
    
    def _load_clause_templates(self):
        """Load individual clause templates."""
        clauses_data = {
            # Grant of Rights Clauses
            'grant_exclusive_en': ClauseTemplate(
                clause_id='grant_exclusive_en',
                clause_type=ClauseType.GRANT_OF_RIGHTS,
                title='Exclusive Grant of Rights',
                template_text="""
                The Licensor hereby grants to the Licensee an exclusive license to {{ usage_rights|join(', ') }} 
                the Work "{{ work_title }}" (the "Work") within the territory of {{ territory }} 
                for the period from {{ start_date }} to {{ end_date }}, subject to the terms and conditions 
                set forth herein.
                """,
                required_variables=['usage_rights', 'work_title', 'territory', 'start_date', 'end_date'],
                optional_variables=['restrictions', 'sub_licensing_rights'],
                jurisdiction_specific=False,
                language=LanguageCode.ENGLISH,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            'grant_non_exclusive_en': ClauseTemplate(
                clause_id='grant_non_exclusive_en',
                clause_type=ClauseType.GRANT_OF_RIGHTS,
                title='Non-Exclusive Grant of Rights',
                template_text="""
                The Licensor hereby grants to the Licensee a non-exclusive license to {{ usage_rights|join(', ') }} 
                the Work "{{ work_title }}" within the territory of {{ territory }} 
                for the duration of {{ duration }}, subject to the terms and conditions herein.
                """,
                required_variables=['usage_rights', 'work_title', 'territory', 'duration'],
                optional_variables=['performance_obligations'],
                jurisdiction_specific=False,
                language=LanguageCode.ENGLISH,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            # Revenue Sharing Clauses
            'revenue_percentage_en': ClauseTemplate(
                clause_id='revenue_percentage_en',
                clause_type=ClauseType.REVENUE_SHARING,
                title='Percentage Revenue Sharing',
                template_text="""
                In consideration for the rights granted herein, the Licensee agrees to pay the Licensor 
                {{ revenue_percentage }}% of all Net Revenues derived from the exploitation of the Work. 
                Net Revenues shall mean gross revenues less actual costs of collection, 
                distribution, and applicable taxes.
                {% if minimum_guarantee %}
                The Licensee guarantees a minimum payment of {{ minimum_guarantee }} {{ currency }} 
                regardless of actual revenues generated.
                {% endif %}
                """,
                required_variables=['revenue_percentage', 'currency'],
                optional_variables=['minimum_guarantee', 'payment_schedule', 'accounting_period'],
                jurisdiction_specific=False,
                language=LanguageCode.ENGLISH,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            # Territory Clauses
            'territory_worldwide_en': ClauseTemplate(
                clause_id='territory_worldwide_en',
                clause_type=ClauseType.TERRITORY,
                title='Worldwide Territory',
                template_text="""
                The territory covered by this Agreement shall be worldwide, including all countries, 
                territories, and possessions, whether now existing or hereafter created.
                """,
                required_variables=[],
                optional_variables=['excluded_territories'],
                jurisdiction_specific=False,
                language=LanguageCode.ENGLISH,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            'territory_specific_en': ClauseTemplate(
                clause_id='territory_specific_en',
                clause_type=ClauseType.TERRITORY,
                title='Specific Territory',
                template_text="""
                The territory covered by this Agreement shall be limited to {{ territories|join(', ') }}.
                The Licensee may not exercise any rights outside of this designated territory.
                """,
                required_variables=['territories'],
                optional_variables=['future_territory_expansion'],
                jurisdiction_specific=False,
                language=LanguageCode.ENGLISH,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            # German Clauses
            'grant_exclusive_de': ClauseTemplate(
                clause_id='grant_exclusive_de',
                clause_type=ClauseType.GRANT_OF_RIGHTS,
                title='Ausschließliche Rechteeinräumung',
                template_text="""
                Der Lizenzgeber räumt dem Lizenznehmer hiermit das ausschließliche Recht ein, 
                das Werk "{{ work_title }}" {{ usage_rights|join(', ') }} zu nutzen 
                im Gebiet {{ territory }} für die Dauer vom {{ start_date }} bis {{ end_date }}, 
                vorbehaltlich der hierin enthaltenen Bedingungen.
                """,
                required_variables=['usage_rights', 'work_title', 'territory', 'start_date', 'end_date'],
                optional_variables=['urheberpersoenlichkeitsrechte'],
                jurisdiction_specific=True,
                language=LanguageCode.GERMAN,
                version='1.0',
                last_updated=datetime.now()
            ),
            
            # Moral Rights Clauses (Germany-specific)
            'moral_rights_germany_de': ClauseTemplate(
                clause_id='moral_rights_germany_de',
                clause_type=ClauseType.MORAL_RIGHTS,
                title='Urheberpersönlichkeitsrechte',
                template_text="""
                Der Lizenzgeber behält alle Urheberpersönlichkeitsrechte am Werk. 
                Der Lizenznehmer verpflichtet sich, das Werk nicht zu entstellen oder zu verändern 
                und den Urheber angemessen zu bezeichnen. Eine Verletzung der Urheberpersönlichkeitsrechte 
                berechtigt den Lizenzgeber zur sofortigen Kündigung dieser Vereinbarung.
                """,
                required_variables=[],
                optional_variables=['attribution_requirements'],
                jurisdiction_specific=True,
                language=LanguageCode.GERMAN,
                version='1.0',
                last_updated=datetime.now()
            )
        }
        
        self.clause_templates = clauses_data
        self.logger.info(f"Loaded {len(clauses_data)} clause templates")
    
    def _load_translations(self):
        """Load translation dictionaries for multi-language support."""
        translations_data = {
            LanguageCode.ENGLISH: {
                'licensor': 'Licensor',
                'licensee': 'Licensee',
                'work': 'Work',
                'territory': 'Territory',
                'duration': 'Duration',
                'revenue': 'Revenue',
                'exclusive': 'Exclusive',
                'non_exclusive': 'Non-Exclusive',
                'worldwide': 'Worldwide',
                'agreement': 'Agreement',
                'terms_and_conditions': 'Terms and Conditions'
            },
            LanguageCode.GERMAN: {
                'licensor': 'Lizenzgeber',
                'licensee': 'Lizenznehmer',
                'work': 'Werk',
                'territory': 'Gebiet',
                'duration': 'Laufzeit',
                'revenue': 'Erlöse',
                'exclusive': 'Ausschließlich',
                'non_exclusive': 'Nicht-ausschließlich',
                'worldwide': 'Weltweit',
                'agreement': 'Vereinbarung',
                'terms_and_conditions': 'Geschäftsbedingungen'
            },
            LanguageCode.FRENCH: {
                'licensor': 'Donneur de licence',
                'licensee': 'Licencié',
                'work': 'Œuvre',
                'territory': 'Territoire',
                'duration': 'Durée',
                'revenue': 'Revenus',
                'exclusive': 'Exclusif',
                'non_exclusive': 'Non-exclusif',
                'worldwide': 'Mondial',
                'agreement': 'Accord',
                'terms_and_conditions': 'Termes et conditions'
            }
        }
        
        self.translations = translations_data
        self.logger.info(f"Loaded translations for {len(translations_data)} languages")
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters for template processing."""
        self.jinja_env.filters['currency_format'] = self._currency_format_filter
        self.jinja_env.filters['date_format'] = self._date_format_filter
        self.jinja_env.filters['legal_format'] = self._legal_format_filter
        self.jinja_env.filters['translate'] = self._translate_filter
    
    def _currency_format_filter(self, amount: float, currency: str = 'USD') -> str:
        """Format currency amounts for legal documents."""
        if currency == 'USD':
            return f"${amount:,.2f}"
        elif currency == 'EUR':
            return f"€{amount:,.2f}"
        elif currency == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    
    def _date_format_filter(self, date_obj: datetime, format_type: str = 'legal') -> str:
        """Format dates for legal documents."""
        if format_type == 'legal':
            return date_obj.strftime("%B %d, %Y")
        elif format_type == 'short':
            return date_obj.strftime("%m/%d/%Y")
        else:
            return date_obj.strftime("%Y-%m-%d")
    
    def _legal_format_filter(self, text: str) -> str:
        """Format text for legal document standards."""
        # Capitalize first letter of sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted_sentences = [s.capitalize() for s in sentences]
        return ' '.join(formatted_sentences)
    
    def _translate_filter(self, key: str, language: LanguageCode) -> str:
        """Translate terms to specified language."""
        language_dict = self.translations.get(language, self.translations[LanguageCode.ENGLISH])
        return language_dict.get(key, key)
    
    async def generate_license_template(
        self,
        license_type: str,
        jurisdiction: str,
        compliance_requirements: Dict[str, Any],
        language: LanguageCode = LanguageCode.ENGLISH
    ) -> Dict[str, Any]:
        """
         Generate complete license template
        
        Args:
            license_type: Type of license to generate
            jurisdiction: Target legal jurisdiction
            compliance_requirements: Legal compliance requirements
            language: Target language for generation
            
        Returns:
            generated_template: Complete license template
        """



        try:
            self.logger.info(f"Generating license template: {license_type} for {jurisdiction}")
            
            # Get base template
            base_template = self.license_templates.get(license_type)
            if not base_template:
                raise ValueError(f"License template {license_type} not found")
            
            # Check language support
            if language not in base_template.supported_languages:
                self.logger.warning(f"Language {language.value} not supported, using English")
                language = LanguageCode.ENGLISH
            
            # Select appropriate clauses based on jurisdiction and compliance
            selected_clauses = await self._select_clauses_for_jurisdiction(
                base_template=base_template,
                jurisdiction=jurisdiction,
                compliance_requirements=compliance_requirements,
                language=language
            )
            
            # Generate template structure
            template_structure = await self._build_template_structure(
                base_template=base_template,
                selected_clauses=selected_clauses,
                language=language
            )
            
            # Create variable definitions
            template_variables = await self._generate_template_variables(
                base_template=base_template,
                selected_clauses=selected_clauses,
                jurisdiction=jurisdiction
            )
            
            # Generate usage instructions
            usage_instructions = await self._generate_usage_instructions(
                template_structure=template_structure,
                template_variables=template_variables,
                language=language
            )
            
            generated_template = {
                'template_id': f"{license_type}_{jurisdiction}_{language.value}_{datetime.now().strftime('%Y%m%d')}",
                'base_template': asdict(base_template),
                'target_jurisdiction': jurisdiction,
                'language': language.value,
                'selected_clauses': [asdict(clause) for clause in selected_clauses],
                'template_structure': template_structure,
                'template_variables': template_variables,
                'usage_instructions': usage_instructions,
                'compliance_notes': compliance_requirements,
                'generated_at': datetime.now().isoformat(),
                'validity_period': (datetime.now() + timedelta(days=365)).isoformat()
            }
            
            self.metrics['templates_generated'] += 1
            
            return generated_template
            
        except Exception as e:
            self.logger.error(f"Failed to generate license template: {e}")
            raise
    
    async def _select_clauses_for_jurisdiction(
        self,
        base_template: LicenseTemplate,
        jurisdiction: str,
        compliance_requirements: Dict[str, Any],
        language: LanguageCode
    ) -> List[ClauseTemplate]:
        """Select appropriate clauses based on jurisdiction requirements."""
        selected_clauses = []
        
        # Always include required clauses
        for clause_type in base_template.required_clauses:
            clause = await self._get_best_clause_for_context(
                clause_type=clause_type,
                jurisdiction=jurisdiction,
                language=language
            )
            if clause:
                selected_clauses.append(clause)
        
        # Add jurisdiction-specific mandatory clauses
        mandatory_clauses = compliance_requirements.get('mandatory_clauses', [])
        for clause_name in mandatory_clauses:
            if clause_name == 'moral_rights' and jurisdiction == 'germany':
                moral_rights_clause = self.clause_templates.get('moral_rights_germany_de')
                if moral_rights_clause and moral_rights_clause not in selected_clauses:
                    selected_clauses.append(moral_rights_clause)
        
        # Add optional clauses based on compliance recommendations
        for clause_type in base_template.optional_clauses:
            if self._is_clause_recommended(clause_type, compliance_requirements):
                clause = await self._get_best_clause_for_context(
                    clause_type=clause_type,
                    jurisdiction=jurisdiction,
                    language=language
                )
                if clause:
                    selected_clauses.append(clause)
        
        return selected_clauses
    
    async def _get_best_clause_for_context(
        self,
        clause_type: ClauseType,
        jurisdiction: str,
        language: LanguageCode
    ) -> Optional[ClauseTemplate]:
        """Get the best clause template for the given context."""
        # Find all clauses of the specified type
        matching_clauses = [
            clause for clause in self.clause_templates.values()
            if clause.clause_type == clause_type
        ]
        
        # Prefer jurisdiction-specific clauses
        jurisdiction_specific = [
            clause for clause in matching_clauses
            if clause.jurisdiction_specific and jurisdiction in clause.clause_id
        ]
        if jurisdiction_specific:
            matching_clauses = jurisdiction_specific
        
        # Prefer clauses in the target language
        language_specific = [
            clause for clause in matching_clauses
            if clause.language == language
        ]
        if language_specific:
            return language_specific[0]
        
        # Fall back to English if target language not available
        english_clauses = [
            clause for clause in matching_clauses
            if clause.language == LanguageCode.ENGLISH
        ]
        
        return english_clauses[0] if english_clauses else None
    
    def _is_clause_recommended(
        self,
        clause_type: ClauseType,
        compliance_requirements: Dict[str, Any]
    ) -> bool:
        """Check if a clause is recommended based on compliance requirements."""
        recommended_clauses = compliance_requirements.get('recommended_clauses', [])
        
        clause_recommendations = {
            ClauseType.WARRANTIES: 'warranties_recommended',
            ClauseType.INDEMNIFICATION: 'indemnification_required',
            ClauseType.GOVERNING_LAW: 'governing_law_required',
            ClauseType.MORAL_RIGHTS: 'moral_rights_protection'
        }
        
        recommendation_key = clause_recommendations.get(clause_type)
        if recommendation_key:
            return compliance_requirements.get(recommendation_key, False)
        
        return clause_type.value in recommended_clauses
    
    async def _build_template_structure(
        self,
        base_template: LicenseTemplate,
        selected_clauses: List[ClauseTemplate],
        language: LanguageCode
    ) -> Dict[str, Any]:
        """Build the complete template structure."""
        structure = base_template.template_structure.copy()
        
        # Add clause mapping
        structure['clause_mapping'] = {}
        for clause in selected_clauses:
            section = self._map_clause_to_section(clause.clause_type)
            if section not in structure['clause_mapping']:
                structure['clause_mapping'][section] = []
            structure['clause_mapping'][section].append({
                'clause_id': clause.clause_id,
                'clause_type': clause.clause_type.value,
                'title': clause.title
            })
        
        # Add language-specific formatting
        structure['formatting'] = {
            'language': language.value,
            'date_format': 'legal' if language == LanguageCode.ENGLISH else 'international',
            'currency_symbol': '$' if language == LanguageCode.ENGLISH else '€',
            'decimal_separator': '.' if language == LanguageCode.ENGLISH else ','
        }
        
        return structure
    
    def _map_clause_to_section(self, clause_type: ClauseType) -> str:
        """Map clause types to document sections."""
        section_mapping = {
            ClauseType.GRANT_OF_RIGHTS: 'grant_of_rights',
            ClauseType.TERRITORY: 'territory_and_duration',
            ClauseType.DURATION: 'territory_and_duration',
            ClauseType.REVENUE_SHARING: 'financial_terms',
            ClauseType.TERMINATION: 'termination',
            ClauseType.WARRANTIES: 'general_provisions',
            ClauseType.INDEMNIFICATION: 'general_provisions',
            ClauseType.GOVERNING_LAW: 'general_provisions',
            ClauseType.MORAL_RIGHTS: 'obligations'
        }
        
        return section_mapping.get(clause_type, 'general_provisions')
    
    async def _generate_template_variables(
        self,
        base_template: LicenseTemplate,
        selected_clauses: List[ClauseTemplate],
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Generate template variable definitions."""
        # Collect all required variables from clauses
        required_variables = set()
        optional_variables = set()
        
        for clause in selected_clauses:
            required_variables.update(clause.required_variables)
            optional_variables.update(clause.optional_variables)
        
        # Generate variable definitions with types and descriptions
        variable_definitions = {}
        
        # Common variables
        common_variables = {
            'licensor_name': {'type': 'string', 'description': 'Full legal name of the licensor'},
            'licensee_name': {'type': 'string', 'description': 'Full legal name of the licensee'},
            'work_title': {'type': 'string', 'description': 'Title of the licensed work'},
            'territory': {'type': 'string', 'description': 'Geographic territory for the license'},
            'duration': {'type': 'string', 'description': 'Duration of the license agreement'},
            'revenue_percentage': {'type': 'number', 'description': 'Revenue share percentage (0-100)'},
            'currency': {'type': 'string', 'description': 'Currency for financial terms'},
            'effective_date': {'type': 'date', 'description': 'License effective date'},
            'usage_rights': {'type': 'array', 'description': 'List of granted usage rights'}
        }
        
        # Add definitions for required variables
        for var in required_variables:
            if var in common_variables:
                variable_definitions[var] = {
                    **common_variables[var],
                    'required': True
                }
        
        # Add definitions for optional variables
        for var in optional_variables:
            if var in common_variables:
                variable_definitions[var] = {
                    **common_variables[var],
                    'required': False
                }
        
        # Add jurisdiction-specific variables
        if jurisdiction == 'germany':
            variable_definitions['gema_required'] = {
                'type': 'boolean',
                'description': 'Whether GEMA licensing is required',
                'required': False
            }
        
        return {
            'variable_definitions': variable_definitions,
            'required_count': len([v for v in variable_definitions.values() if v.get('required', False)]),
            'optional_count': len([v for v in variable_definitions.values() if not v.get('required', False)]),
            'total_variables': len(variable_definitions)
        }
    
    async def _generate_usage_instructions(
        self,
        template_structure: Dict[str, Any],
        template_variables: Dict[str, Any],
        language: LanguageCode
    ) -> Dict[str, Any]:
        """Generate usage instructions for the template."""
        instructions = {
            'overview': self._get_template_overview(language),
            'variable_instructions': self._get_variable_instructions(template_variables, language),
            'customization_guide': self._get_customization_guide(template_structure, language),
            'legal_notices': self._get_legal_notices(language),
            'best_practices': self._get_best_practices(language)
        }
        
        return instructions
    
    def _get_template_overview(self, language: LanguageCode) -> str:
        """Get template overview in specified language."""
        overviews = {
            LanguageCode.ENGLISH: "This template provides a legally compliant license agreement framework. Fill in the required variables and customize clauses as needed for your specific use case.",
            LanguageCode.GERMAN: "Diese Vorlage bietet einen rechtlich konformen Rahmen für Lizenzvereinbarungen. Füllen Sie die erforderlichen Variablen aus und passen Sie die Klauseln nach Bedarf an.",
            LanguageCode.FRENCH: "Ce modèle fournit un cadre d'accord de licence juridiquement conforme. Remplissez les variables requises et personnalisez les clauses selon vos besoins."
        }
        
        return overviews.get(language, overviews[LanguageCode.ENGLISH])
    
    def _get_variable_instructions(self, template_variables: Dict[str, Any], language: LanguageCode) -> List[str]:
        """Get variable filling instructions."""
        instructions = []
        variable_definitions = template_variables.get('variable_definitions', {})
        
        if language == LanguageCode.ENGLISH:
            instructions.append(f"Fill in all {template_variables.get('required_count', 0)} required variables")
            instructions.append("Optional variables can be left blank if not applicable")
            instructions.append("Ensure all dates are in the correct format")
            instructions.append("Revenue percentages should be entered as numbers (e.g., 70 for 70%)")
        elif language == LanguageCode.GERMAN:
            instructions.append(f"Füllen Sie alle {template_variables.get('required_count', 0)} erforderlichen Variablen aus")
            instructions.append("Optionale Variablen können leer gelassen werden, falls nicht zutreffend")
            instructions.append("Stellen Sie sicher, dass alle Daten im korrekten Format vorliegen")
            instructions.append("Umsatzprozentsätze sollten als Zahlen eingegeben werden (z.B. 70 für 70%)")
        
        return instructions
    
    def _get_customization_guide(self, template_structure: Dict[str, Any], language: LanguageCode) -> List[str]:
        """Get template customization guidelines."""
        if language == LanguageCode.ENGLISH:
            return [
                "Review all clauses for applicability to your situation",
                "Consult legal counsel before finalizing any agreement",
                "Ensure compliance with local laws and regulations",
                "Consider adding jurisdiction-specific clauses as needed"
            ]
        elif language == LanguageCode.GERMAN:
            return [
                "Überprüfen Sie alle Klauseln auf Anwendbarkeit für Ihre Situation",
                "Konsultieren Sie Rechtsberatung vor Abschluss einer Vereinbarung",
                "Stellen Sie die Einhaltung lokaler Gesetze und Vorschriften sicher",
                "Erwägen Sie die Hinzufügung jurisdiktionsspezifischer Klauseln nach Bedarf"
            ]
        else:
            return self._get_customization_guide(template_structure, LanguageCode.ENGLISH)
    
    def _get_legal_notices(self, language: LanguageCode) -> List[str]:
        """Get legal disclaimer notices."""
        if language == LanguageCode.ENGLISH:
            return [
                "This template is for informational purposes only",
                "Always consult qualified legal counsel",
                "Laws vary by jurisdiction - ensure local compliance",
                "Regular updates may be required for continued compliance"
            ]
        elif language == LanguageCode.GERMAN:
            return [
                "Diese Vorlage dient nur zu Informationszwecken",
                "Konsultieren Sie immer qualifizierte Rechtsberatung",
                "Gesetze variieren je nach Rechtsgebiet - stellen Sie lokale Compliance sicher",
                "Regelmäßige Updates können für fortgesetzte Compliance erforderlich sein"
            ]
        else:
            return self._get_legal_notices(LanguageCode.ENGLISH)
    
    def _get_best_practices(self, language: LanguageCode) -> List[str]:
        """Get template best practices."""
        if language == LanguageCode.ENGLISH:
            return [
                "Keep detailed records of all license agreements",
                "Implement regular compliance reviews",
                "Maintain clear communication with all parties",
                "Consider automated monitoring for large-scale licensing"
            ]
        elif language == LanguageCode.GERMAN:
            return [
                "Führen Sie detaillierte Aufzeichnungen aller Lizenzvereinbarungen",
                "Implementieren Sie regelmäßige Compliance-Überprüfungen",
                "Halten Sie klare Kommunikation mit allen Parteien aufrecht",
                "Erwägen Sie automatisierte Überwachung für große Lizenzierung"
            ]
        else:
            return self._get_best_practices(LanguageCode.ENGLISH)
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available license templates."""



        return [
            {
                'template_id': template.template_id,
                'category': template.category.value,
                'name': template.name,
                'description': template.description,
                'supported_languages': [lang.value for lang in template.supported_languages],
                'target_jurisdictions': template.target_jurisdictions,
                'compliance_level': template.compliance_level,
                'industry_standard': template.industry_standard
            }
            for template in self.license_templates.values()
        ]
    
    def get_template_metrics(self) -> Dict[str, Any]:
        """Get template engine performance metrics."""



        return {
            **self.metrics,
            'available_templates': len(self.license_templates),
            'available_clauses': len(self.clause_templates),
            'supported_languages': [lang.value for lang in self.supported_languages],
            'timestamp': datetime.now().isoformat()
        }
