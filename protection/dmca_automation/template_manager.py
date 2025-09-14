"""Template Manager

Advanced template management system for DMCA notices and legal documents
with multi-jurisdiction support, dynamic content generation, and compliance validation.

Author: Fahed Mlaiel
Email: mlaiel@live.de

⚠️ COPYRIGHT WARNING ⚠️
Unauthorized copying or distribution prohibited. All rights reserved (c) 2025 Fahed Mlaiel
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import jinja2
from jinja2 import Environment, FileSystemLoader, Template

from ...core.database import get_database
from ...core.exceptions import ContentProtectionError
from ...utils.validation import ValidationService
from ...utils.localization import LocalizationService
from ..models import DMCATemplate, TemplateVariables

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """
Types of legal templates"""

    DMCA_TAKEDOWN = "dmca_takedown"
    DMCA_COUNTER_NOTICE = "dmca_counter_notice"
    COPYRIGHT_NOTICE = "copyright_notice"
    CEASE_DESIST = "cease_desist"
    FOLLOW_UP_NOTICE = "follow_up_notice"
    ESCALATION_NOTICE = "escalation_notice"
    COMPLIANCE_VERIFICATION = "compliance_verification"
    LEGAL_DEMAND = "legal_demand"
    SETTLEMENT_OFFER = "settlement_offer"
    COURT_FILING = "court_filing"


class TemplateFormat(Enum):
    """Template output formats"""

    HTML = "html"
    PDF = "pdf"
    PLAIN_TEXT = "plain_text"
    DOCX = "docx"
    RTF = "rtf"
    JSON = "json"


class Jurisdiction(Enum):
    """Legal jurisdictions with specific requirements"""

    US_FEDERAL = "us_federal"
    US_CALIFORNIA = "us_california"
    US_NEW_YORK = "us_new_york"
    EU_GENERAL = "eu_general"
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GERMANY = "germany"
    FRANCE = "france"
    JAPAN = "japan"
    SINGAPORE = "singapore"
    BRAZIL = "brazil"
    MEXICO = "mexico"
    INDIA = "india"
    SOUTH_AFRICA = "south_africa"
    INTERNATIONAL = "international"


@dataclass
class TemplateMetadata:
    """Template metadata and configuration"""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    jurisdiction: Jurisdiction
    language: str
    version: str
    created_at: datetime
    updated_at: datetime
    author: str
    legal_review_date: Optional[datetime] = None
    compliance_verified: bool = False
    usage_count: int = 0
    success_rate: float = 0.0
    platform_compatibility: List[str] = field(default_factory=list)
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)


@dataclass
class TemplateValidationResult:
    """
Template validation result"""
    is_valid: bool
    validation_score: float
    compliance_issues: List[str]
    recommendations: List[str]
    legal_risks: List[str]
    formatting_issues: List[str]


@dataclass
class GeneratedDocument:
    """
Generated document result"""
    document_id: str
    template_id: str
    content: str
    format: TemplateFormat
    variables_used: Dict[str, Any]
    generated_at: datetime
    validation_result: TemplateValidationResult
    metadata: Dict[str, Any]


class TemplateManager:
    """
    Advanced template management system for legal documents
    
    Features:
    - Multi-jurisdiction template support
    - Dynamic content generation
    - Compliance validation
    - Version management
    - Performance tracking
    - Localization support
    - Platform-specific formatting
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """
Initialize template manager"""
        self.config = config or {}
        self.db = get_database()
        self.validation_service = ValidationService(config)
        self.localization_service = LocalizationService(config)
        self.logger = logger
        
        # Template directory setup
        self.template_dir = Path(self.config.get('template_directory', 'templates'))
        self.template_dir.mkdir(exist_ok=True)
        
        # Jinja2 environment setup
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Custom filters for legal documents
        self.jinja_env.filters.update({
            'legal_format': self._legal_format_filter,
            'jurisdiction_format': self._jurisdiction_format_filter,
            'date_legal': self._date_legal_filter,
            'currency_format': self._currency_format_filter,
            'escape_legal': self._escape_legal_filter
        })
        
        # Jurisdiction-specific requirements
        self.jurisdiction_requirements = {
            Jurisdiction.US_FEDERAL: {
                'required_fields': ['copyright_owner', 'infringing_material', 'contact_info'],
                'format_requirements': ['dmca_compliance', 'good_faith_statement'],
                'signature_required': True,
                'notarization_required': False
            },
            Jurisdiction.EU_GENERAL: {
                'required_fields': ['data_subject', 'legal_basis', 'contact_info'],
                'format_requirements': ['gdpr_compliance', 'data_protection'],
                'signature_required': True,
                'notarization_required': False
            },
            Jurisdiction.UK: {
                'required_fields': ['copyright_owner', 'infringing_content', 'legal_basis'],
                'format_requirements': ['uk_copyright_act', 'prescribed_format'],
                'signature_required': True,
                'notarization_required': False
            }
        }
        
        # Platform-specific formatting rules
        self.platform_formatting = {
            'youtube': {
                'max_length': 5000,
                'required_format': 'html',
                'special_fields': ['video_url', 'timestamp_ranges']
            },
            'facebook': {
                'max_length': 3000,
                'required_format': 'plain_text',
                'special_fields': ['post_url', 'user_profile']
            },
            'instagram': {
                'max_length': 2000,
                'required_format': 'plain_text',
                'special_fields': ['media_url', 'username']
            },
            'tiktok': {
                'max_length': 1000,
                'required_format': 'plain_text',
                'special_fields': ['video_url', 'creator_username']
            }
        }
    
    async def create_template(self, 
                            template_data: Dict[str, Any],
                            template_content: str) -> Dict[str, Any]:
        """
        Create new legal document template
        
        Args:
            template_data: Template metadata and configuration
            template_content: Template content with Jinja2 variables
            
        Returns:
            Created template information
        """
        try:
            self.logger.info(f"Creating new template: {template_data.get('name')}")
            
            # Generate template ID
            template_id = str(uuid.uuid4())
            
            # Validate template content
            validation_result = await self._validate_template_content(
                template_content, template_data
            )
            
            if not validation_result.is_valid:
                raise ContentProtectionError(
                    f"Template validation failed: {validation_result.compliance_issues}"
                )
            
            # Create template metadata
            metadata = TemplateMetadata(
                template_id=template_id,
                name=template_data['name'],
                description=template_data.get('description', ''),
                template_type=TemplateType(template_data['template_type']),
                jurisdiction=Jurisdiction(template_data['jurisdiction']),
                language=template_data.get('language', 'en'),
                version=template_data.get('version', '1.0'),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                author=template_data.get('author', 'system'),
                platform_compatibility=template_data.get('platform_compatibility', []),
                required_variables=await self._extract_required_variables(template_content),
                optional_variables=await self._extract_optional_variables(template_content)
            )
            
            # Save template file
            template_file_path = self.template_dir / f"{template_id}.j2"
            with open(template_file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Store metadata in database
            await self._store_template_metadata(metadata)
            
            # Generate template preview
            preview = await self._generate_template_preview(template_id, template_content)
            
            return {
                'success': True,
                'template_id': template_id,
                'metadata': metadata.__dict__,
                'validation_result': validation_result.__dict__,
                'preview': preview,
                'file_path': str(template_file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Template creation failed: {str(e)}")
            raise ContentProtectionError(f"Template creation failed: {str(e)}")
    
    async def generate_document(self, 
                              template_id: str,
                              variables: Dict[str, Any],
                              output_format: TemplateFormat = TemplateFormat.HTML,
                              platform_id: Optional[str] = None) -> GeneratedDocument:
        """
        Generate document from template with provided variables
        
        Args:
            template_id: ID of the template to use
            variables: Variables to populate in the template
            output_format: Desired output format
            platform_id: Optional platform for platform-specific formatting
            
        Returns:
            Generated document with validation
        """
        try:
            self.logger.info(f"Generating document from template: {template_id}")
            
            # Load template metadata
            metadata = await self._load_template_metadata(template_id)
            
            # Load template content
            template_content = await self._load_template_content(template_id)
            
            # Validate required variables
            missing_vars = await self._validate_template_variables(metadata, variables)
            if missing_vars:
                raise ContentProtectionError(f"Missing required variables: {missing_vars}")
            
            # Apply jurisdiction-specific processing
            processed_variables = await self._process_jurisdiction_variables(
                variables, metadata.jurisdiction
            )
            
            # Apply platform-specific formatting if specified
            if platform_id:
                processed_variables = await self._apply_platform_formatting(
                    processed_variables, platform_id
                )
            
            # Render template
            template = self.jinja_env.from_string(template_content)
            rendered_content = template.render(**processed_variables)
            
            # Convert to desired format
            formatted_content = await self._convert_to_format(rendered_content, output_format)
            
            # Validate generated document
            validation_result = await self._validate_generated_document(
                formatted_content, metadata, processed_variables
            )
            
            # Create document record
            document = GeneratedDocument(
                document_id=str(uuid.uuid4()),
                template_id=template_id,
                content=formatted_content,
                format=output_format,
                variables_used=processed_variables,
                generated_at=datetime.now(timezone.utc),
                validation_result=validation_result,
                metadata={
                    'template_name': metadata.name,
                    'jurisdiction': metadata.jurisdiction.value,
                    'platform_id': platform_id,
                    'generation_version': '2.0'
                }
            )
            
            # Store document record
            await self._store_generated_document(document)
            
            # Update template usage statistics
            await self._update_template_usage(template_id)
            
            return document
            
        except Exception as e:
            self.logger.error(f"Document generation failed: {str(e)}")
            raise ContentProtectionError(f"Document generation failed: {str(e)}")
    
    async def get_template_library(self, 
                                 filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get available templates with optional filtering
        
        Args:
            filters: Optional filters for template search
            
        Returns:
            Template library with metadata
        """
        try:
            self.logger.info("Retrieving template library")
            
            # Apply default filters
            filters = filters or {}
            
            # Query templates from database
            templates = await self._query_templates(filters)
            
            # Group templates by category
            categorized_templates = {
                'dmca_notices': [],
                'legal_documents': [],
                'compliance_forms': [],
                'custom_templates': []
            }
            
            for template in templates:
                category = await self._categorize_template(template)
                if category in categorized_templates:
                    categorized_templates[category].append(template)
            
            # Calculate library statistics
            library_stats = await self._calculate_library_statistics(templates)
            
            return {
                'total_templates': len(templates),
                'categories': categorized_templates,
                'statistics': library_stats,
                'jurisdictions_supported': list(set(t.jurisdiction.value for t in templates)),
                'languages_supported': list(set(t.language for t in templates)),
                'most_used_templates': await self._get_most_used_templates(),
                'recent_templates': await self._get_recent_templates()
            }
            
        except Exception as e:
            self.logger.error(f"Template library retrieval failed: {str(e)}")
            raise ContentProtectionError(f"Library retrieval failed: {str(e)}")
    
    async def update_template(self, 
                            template_id: str,
                            updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing template with new content or metadata
        
        Args:
            template_id: ID of template to update
            updates: Updates to apply
            
        Returns:
            Update result
        """
        try:
            self.logger.info(f"Updating template: {template_id}")
            
            # Load current template
            current_metadata = await self._load_template_metadata(template_id)
            current_content = await self._load_template_content(template_id)
            
            # Create backup
            backup_id = await self._create_template_backup(template_id)
            
            # Apply updates to metadata
            updated_metadata = await self._apply_metadata_updates(current_metadata, updates)
            
            # Apply content updates if provided
            updated_content = current_content
            if 'content' in updates:
                updated_content = updates['content']
                
                # Validate updated content
                validation_result = await self._validate_template_content(
                    updated_content, updated_metadata.__dict__
                )
                
                if not validation_result.is_valid:
                    # Restore from backup
                    await self._restore_template_from_backup(template_id, backup_id)
                    raise ContentProtectionError(
                        f"Template validation failed: {validation_result.compliance_issues}"
                    )
            
            # Update version number
            updated_metadata.version = await self._increment_version(updated_metadata.version)
            updated_metadata.updated_at = datetime.now(timezone.utc)
            
            # Save updated template
            await self._save_template_content(template_id, updated_content)
            await self._update_template_metadata(updated_metadata)
            
            # Generate change log
            change_log = await self._generate_change_log(
                current_metadata, updated_metadata, current_content, updated_content
            )
            
            return {
                'success': True,
                'template_id': template_id,
                'previous_version': current_metadata.version,
                'new_version': updated_metadata.version,
                'backup_id': backup_id,
                'change_log': change_log,
                'validation_passed': True
            }
            
        except Exception as e:
            self.logger.error(f"Template update failed: {str(e)}")
            raise ContentProtectionError(f"Template update failed: {str(e)}")
    
    async def validate_template_compliance(self, 
                                         template_id: str,
                                         jurisdiction: Optional[Jurisdiction] = None) -> Dict[str, Any]:
        """
        Validate template compliance with legal requirements
        
        Args:
            template_id: Template to validate
            jurisdiction: Optional specific jurisdiction to validate against
            
        Returns:
            Comprehensive compliance validation
        """
        try:
            self.logger.info(f"Validating template compliance: {template_id}")
            
            # Load template
            metadata = await self._load_template_metadata(template_id)
            content = await self._load_template_content(template_id)
            
            # Use template's jurisdiction if not specified
            target_jurisdiction = jurisdiction or metadata.jurisdiction
            
            # Get jurisdiction requirements
            requirements = self.jurisdiction_requirements.get(target_jurisdiction, {})
            
            # Validate structure
            structure_validation = await self._validate_template_structure(content, requirements)
            
            # Validate legal compliance
            legal_validation = await self._validate_legal_compliance(content, target_jurisdiction)
            
            # Validate formatting
            format_validation = await self._validate_template_formatting(content, metadata)
            
            # Check for potential legal issues
            legal_issues = await self._identify_legal_issues(content, target_jurisdiction)
            
            # Calculate overall compliance score
            compliance_score = await self._calculate_compliance_score(
                structure_validation, legal_validation, format_validation
            )
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                structure_validation, legal_validation, format_validation, legal_issues
            )
            
            return {
                'template_id': template_id,
                'jurisdiction': target_jurisdiction.value,
                'compliance_score': compliance_score,
                'overall_status': 'compliant' if compliance_score >= 0.8 else 'non_compliant',
                'structure_validation': structure_validation,
                'legal_validation': legal_validation,
                'format_validation': format_validation,
                'identified_issues': legal_issues,
                'recommendations': recommendations,
                'last_validated': datetime.now(timezone.utc).isoformat(),
                'requires_legal_review': compliance_score < 0.7
            }
            
        except Exception as e:
            self.logger.error(f"Template compliance validation failed: {str(e)}")
            raise ContentProtectionError(f"Compliance validation failed: {str(e)}")
    
    # Custom Jinja2 filters
    
    def _legal_format_filter(self, value: str) -> str:
        """Format text for legal documents"""
        if not value:
            return ""
        
        # Capitalize first letter of each sentence
        sentences = value.split('. ')
        formatted_sentences = [s.strip().capitalize() for s in sentences if s.strip()]
        return '. '.join(formatted_sentences)
    
    def _jurisdiction_format_filter(self, value: str, jurisdiction: str) -> str:
        """Format content based on jurisdiction requirements"""
        if jurisdiction == Jurisdiction.US_FEDERAL.value:
            # US formatting: use "shall" instead of "will"
            value = value.replace(' will ', ' shall ')
            value = value.replace(' Will ', ' Shall ')
        elif jurisdiction == Jurisdiction.UK.value:
            # UK formatting: use British spelling
            value = value.replace('organization', 'organisation')
            value = value.replace('authorize', 'authorise')
        
        return value
    
    def _date_legal_filter(self, value: datetime, jurisdiction: str = 'us') -> str:
        """Format dates for legal documents"""
        if jurisdiction.startswith('us'):
            return value.strftime("%B %d, %Y")  # "January 1, 2025"
        elif jurisdiction == 'uk':
            return value.strftime("%d %B %Y")   # "1 January 2025"
        else:
            return value.strftime("%Y-%m-%d")   # "2025-01-01"
    
    def _currency_format_filter(self, value: float, currency: str = 'USD') -> str:
        """Format currency for legal documents"""
        if currency == 'USD':
            return f"${value:,.2f}"
        elif currency == 'EUR':
            return f"€{value:,.2f}"
        elif currency == 'GBP':
            return f"£{value:,.2f}"
        else:
            return f"{value:,.2f} {currency}"
    
    def _escape_legal_filter(self, value: str) -> str:
        """Escape special characters for legal documents"""
        # Escape common problematic characters
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        return value
    
    # Private helper methods
    
    async def _validate_template_content(self, 
                                       content: str,
                                       template_data: Dict[str, Any]) -> TemplateValidationResult:
        """Validate template content for legal compliance"""
        issues = []
        recommendations = []
        risks = []
        formatting_issues = []
        
        # Check for required legal elements
        if template_data.get('template_type') == TemplateType.DMCA_TAKEDOWN.value:
            required_elements = [
                'copyright owner', 'infringing material', 'good faith belief',
                'penalty of perjury', 'signature'
            ]
            
            for element in required_elements:
                if element.lower() not in content.lower():
                    issues.append(f"Missing required element: {element}")
        
        # Check template syntax
        try:
            template = self.jinja_env.from_string(content)
            # Try to render with empty context to check for syntax errors
            template.render()
        except Exception as e:
            formatting_issues.append(f"Template syntax error: {str(e)}")
        
        # Calculate validation score
        total_checks = len(required_elements) + 1  # +1 for syntax check
        failed_checks = len(issues) + len(formatting_issues)
        validation_score = max(0.0, (total_checks - failed_checks) / total_checks)
        
        return TemplateValidationResult(
            is_valid=len(issues) == 0 and len(formatting_issues) == 0,
            validation_score=validation_score,
            compliance_issues=issues,
            recommendations=recommendations,
            legal_risks=risks,
            formatting_issues=formatting_issues
        )
    
    async def _extract_required_variables(self, content: str) -> List[str]:
        """Extract required template variables"""
        import re
        
        # Find all {{ variable }} patterns
        variable_pattern = r'\{\{\s*([^}|]+)(?:\|[^}]*)?\s*\}\}'
        variables = re.findall(variable_pattern, content)
        
        # Clean and deduplicate
        cleaned_vars = []
        for var in variables:
            clean_var = var.strip().split('.')[0]  # Remove property access
            if clean_var not in cleaned_vars:
                cleaned_vars.append(clean_var)
        
        return cleaned_vars
    
    async def _extract_optional_variables(self, content: str) -> List[str]:
        """
Extract optional template variables (with default values)"""
        import re
        
        # Find variables with default values: {{ variable|default("value") }}
        default_pattern = r'\{\{\s*([^}|]+)\|default\([^)]*\)\s*\}\}'
        optional_vars = re.findall(default_pattern, content)
        
        return [var.strip() for var in optional_vars]
