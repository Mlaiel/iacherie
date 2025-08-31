"""IA-Influencer Agent - Workflow Template Manager

Enterprise-grade workflow template management system for content creators.
Provides pre-built, customizable workflow templates for common use cases.

Key Features:
- Pre-built workflow templates
- Template customization engine
- Template versioning and inheritance
- Industry-specific templates
- AI-powered template optimization
- Template marketplace integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from pathlib import Path
import yaml
from jinja2 import Environment, BaseLoader, meta
import jsonschema
from semantic_version import Version

from ..base import BaseAgent


class TemplateType(Enum):
    """Template type enumeration."""
    CONTENT_CREATION = "content_creation"
    CONTENT_PROTECTION = "content_protection"
    SOCIAL_MEDIA_PUBLISHING = "social_media_publishing"
    MUSIC_PRODUCTION = "music_production"
    VIDEO_PROCESSING = "video_processing"
    AUDIO_PROCESSING = "audio_processing"
    SEO_OPTIMIZATION = "seo_optimization"
    ANALYTICS_REPORTING = "analytics_reporting"
    COLLABORATION_WORKFLOW = "collaboration_workflow"
    MONETIZATION_PIPELINE = "monetization_pipeline"
    BRAND_MANAGEMENT = "brand_management"
    INFLUENCER_OUTREACH = "influencer_outreach"


class TemplateCategory(Enum):
    """Template category enumeration."""
    MUSICIAN = "musician"
    PODCASTER = "podcaster"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    ARTIST = "artist"
    COMEDIAN = "comedian"
    ENTREPRENEUR = "entrepreneur"
    BRAND = "brand"


@dataclass
class TemplateMetadata:
    """Template metadata information."""
    id: str
    name: str
    description: str
    version: str
    author: str
    category: TemplateCategory
    template_type: TemplateType
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    rating: float = 0.0
    complexity_level: str = "intermediate"  # beginner, intermediate, advanced
    estimated_duration: int = 0  # minutes
    required_integrations: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class WorkflowTemplate:
    """Complete workflow template definition."""
    metadata: TemplateMetadata
    workflow_definition: Dict[str, Any]
    parameters: Dict[str, Any]
    validation_schema: Dict[str, Any]
    documentation: str
    examples: List[Dict[str, Any]] = field(default_factory=list)
    customization_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateInstance:
    """Template instance with user customizations."""
    id: str
    template_id: str
    user_id: str
    name: str
    customizations: Dict[str, Any]
    created_at: datetime
    last_used: datetime
    usage_count: int = 0


class WorkflowTemplateManager(BaseAgent):
    """
    Advanced workflow template manager for content creator workflows.
    
    This manager provides comprehensive template management including
    creation, customization, versioning, and optimization capabilities.
    """
    def __init__(self, template_directory: Optional[str] = None):
        """Initialize the template manager."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Template storage
        self.template_directory = Path(template_directory) if template_directory else Path("./templates")
        self.template_directory.mkdir(exist_ok=True)
        
        # Template registry
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.template_instances: Dict[str, TemplateInstance] = {}
        
        # Template validation schemas
        self.validation_schemas = self._load_validation_schemas()
        
        # Jinja2 environment for template rendering
        self.template_env = Environment(loader=BaseLoader())
        
        # Load built-in templates
        self._initialize_builtin_templates()
        
        # Template analytics
        self.template_analytics = {
            'total_templates': 0,
            'total_instances': 0,
            'popular_templates': {},
            'usage_patterns': {},
            'optimization_suggestions': []
        }

    async def create_template(
        self,
        name: str,
        description: str,
        category: TemplateCategory,
        template_type: TemplateType,
        workflow_definition: Dict[str, Any],
        author: str = "System",
        **kwargs
    ) -> str:
        """
        Create a new workflow template.
        
        Args:
            name: Template name
            description: Template description
            category: Template category
            template_type: Template type
            workflow_definition: Workflow definition
            author: Template author
            **kwargs: Additional metadata
            
        Returns:
            str: Template ID
        """
        try:
            template_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = TemplateMetadata(
                id=template_id,
                name=name,
                description=description,
                version="1.0.0",
                author=author,
                category=category,
                template_type=template_type,
                tags=kwargs.get('tags', []),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                complexity_level=kwargs.get('complexity_level', 'intermediate'),
                estimated_duration=kwargs.get('estimated_duration', 30),
                required_integrations=kwargs.get('required_integrations', []),
                prerequisites=kwargs.get('prerequisites', [])
            )
            
            # Validate workflow definition
            validation_result = await self._validate_workflow_definition(workflow_definition)
            if not validation_result['valid']:
                raise ValueError(f"Invalid workflow definition: {validation_result['errors']}")
            
            # Generate validation schema
            validation_schema = await self._generate_validation_schema(workflow_definition)
            
            # Generate parameters schema
            parameters = await self._extract_template_parameters(workflow_definition)
            
            # Create template
            template = WorkflowTemplate(
                metadata=metadata,
                workflow_definition=workflow_definition,
                parameters=parameters,
                validation_schema=validation_schema,
                documentation=kwargs.get('documentation', ''),
                examples=kwargs.get('examples', []),
                customization_options=kwargs.get('customization_options', {})
            )
            
            # Store template
            self.templates[template_id] = template
            await self._save_template_to_disk(template)
            
            # Update analytics
            self.template_analytics['total_templates'] += 1
            
            self.logger.info(f"Created template: {name} ({template_id})")
            return template_id
            
        except Exception as e:
            self.logger.error(f"Error creating template: {str(e)}")
            raise

    async def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get template by ID."""
        try:
            if template_id in self.templates:
                return self.templates[template_id]
            
            # Try to load from disk
            template = await self._load_template_from_disk(template_id)
            if template:
                self.templates[template_id] = template
                return template
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting template {template_id}: {str(e)}")
            return None

    async def search_templates(
        self,
        category: Optional[TemplateCategory] = None,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None,
        complexity_level: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search templates based on criteria.
        
        Args:
            category: Template category filter
            template_type: Template type filter
            tags: Tags filter
            complexity_level: Complexity level filter
            query: Text search query
            
        Returns:
            List of matching template metadata
        """
        try:
            matching_templates = []
            
            for template in self.templates.values():
                metadata = template.metadata
                
                # Apply filters
                if category and metadata.category != category:
                    continue
                
                if template_type and metadata.template_type != template_type:
                    continue
                
                if complexity_level and metadata.complexity_level != complexity_level:
                    continue
                
                if tags:
                    if not any(tag in metadata.tags for tag in tags):
                        continue
                
                if query:
                    query_lower = query.lower()
                    if (query_lower not in metadata.name.lower() and
                        query_lower not in metadata.description.lower() and
                        not any(query_lower in tag.lower() for tag in metadata.tags)):
                        continue
                
                # Add to results
                matching_templates.append({
                    'id': metadata.id,
                    'name': metadata.name,
                    'description': metadata.description,
                    'category': metadata.category.value,
                    'template_type': metadata.template_type.value,
                    'version': metadata.version,
                    'author': metadata.author,
                    'tags': metadata.tags,
                    'complexity_level': metadata.complexity_level,
                    'estimated_duration': metadata.estimated_duration,
                    'rating': metadata.rating,
                    'usage_count': metadata.usage_count,
                    'created_at': metadata.created_at.isoformat()
                })
            
            # Sort by relevance (usage count and rating)
            matching_templates.sort(
                key=lambda t: (t['usage_count'], t['rating']),
                reverse=True
            )
            
            return matching_templates
            
        except Exception as e:
            self.logger.error(f"Error searching templates: {str(e)}")
            return []

    async def instantiate_template(
        self,
        template_id: str,
        user_id: str,
        instance_name: str,
        customizations: Dict[str, Any] = None
    ) -> str:
        """
        Create an instance of a template with user customizations.
        
        Args:
            template_id: Template ID to instantiate
            user_id: User creating the instance
            instance_name: Name for the instance
            customizations: User customizations
            
        Returns:
            str: Instance ID
        """
        try:
            # Get template
            template = await self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Validate customizations
            if customizations:
                validation_result = await self._validate_customizations(
                    template, customizations
                )
                if not validation_result['valid']:
                    raise ValueError(f"Invalid customizations: {validation_result['errors']}")
            
            # Create instance
            instance_id = str(uuid.uuid4())
            instance = TemplateInstance(
                id=instance_id,
                template_id=template_id,
                user_id=user_id,
                name=instance_name,
                customizations=customizations or {},
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            
            # Store instance
            self.template_instances[instance_id] = instance
            
            # Update template usage
            template.metadata.usage_count += 1
            
            # Update analytics
            self.template_analytics['total_instances'] += 1
            self._update_usage_patterns(template_id, user_id)
            
            self.logger.info(f"Created template instance: {instance_name} ({instance_id})")
            return instance_id
            
        except Exception as e:
            self.logger.error(f"Error instantiating template: {str(e)}")
            raise

    async def customize_template(
        self,
        template_id: str,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply customizations to a template and return the customized workflow.
        
        Args:
            template_id: Template ID
            customizations: Customizations to apply
            
        Returns:
            Dict containing customized workflow definition
        """
        try:
            # Get template
            template = await self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Validate customizations
            validation_result = await self._validate_customizations(template, customizations)
            if not validation_result['valid']:
                raise ValueError(f"Invalid customizations: {validation_result['errors']}")
            
            # Apply customizations
            customized_workflow = await self._apply_customizations(
                template.workflow_definition.copy(),
                customizations,
                template.parameters
            )
            
            return {
                'workflow_definition': customized_workflow,
                'metadata': asdict(template.metadata),
                'applied_customizations': customizations
            }
            
        except Exception as e:
            self.logger.error(f"Error customizing template: {str(e)}")
            raise

    async def get_template_recommendations(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get template recommendations for a user based on their profile and usage history.
        
        Args:
            user_id: User ID
            user_profile: User profile information
            
        Returns:
            List of recommended templates
        """
        try:
            recommendations = []
            
            # Get user's previous template instances
            user_instances = [
                instance for instance in self.template_instances.values()
                if instance.user_id == user_id
            ]
            
            # Analyze user preferences
            user_categories = set()
            user_types = set()
            
            for instance in user_instances:
                template = await self.get_template(instance.template_id)
                if template:
                    user_categories.add(template.metadata.category)
                    user_types.add(template.metadata.template_type)
            
            # Score templates based on user profile
            for template in self.templates.values():
                score = 0.0
                
                # Category matching
                if template.metadata.category in user_categories:
                    score += 3.0
                
                # Type matching
                if template.metadata.template_type in user_types:
                    score += 2.0
                
                # Popularity score
                score += min(2.0, template.metadata.usage_count / 100.0)
                
                # Rating score
                score += template.metadata.rating / 5.0
                
                # Profile matching
                profile_tags = user_profile.get('interests', [])
                matching_tags = set(template.metadata.tags) & set(profile_tags)
                score += len(matching_tags) * 0.5
                
                # Complexity level matching
                user_level = user_profile.get('expertise_level', 'intermediate')
                if template.metadata.complexity_level == user_level:
                    score += 1.0
                
                recommendations.append({
                    'template_id': template.metadata.id,
                    'name': template.metadata.name,
                    'description': template.metadata.description,
                    'category': template.metadata.category.value,
                    'template_type': template.metadata.template_type.value,
                    'score': score,
                    'rating': template.metadata.rating,
                    'usage_count': template.metadata.usage_count
                })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:10]
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def _initialize_builtin_templates(self):
        """Initialize built-in workflow templates."""
        try:
            builtin_templates = [
                {
                    'name': 'Music Release Workflow',
                    'description': 'Complete workflow for music production, protection, and distribution',
                    'category': TemplateCategory.MUSICIAN,
                    'template_type': TemplateType.MUSIC_PRODUCTION,
                    'workflow_definition': self._create_music_release_workflow(),
                    'tags': ['music', 'release', 'spotify', 'protection'],
                    'complexity_level': 'advanced',
                    'estimated_duration': 120
                },
                {
                    'name': 'Social Media Content Pipeline',
                    'description': 'Automated content creation and publishing for social media',
                    'category': TemplateCategory.INFLUENCER,
                    'template_type': TemplateType.SOCIAL_MEDIA_PUBLISHING,
                    'workflow_definition': self._create_social_media_workflow(),
                    'tags': ['social-media', 'automation', 'content'],
                    'complexity_level': 'intermediate',
                    'estimated_duration': 45
                },
                {
                    'name': 'Video Content Protection',
                    'description': 'Comprehensive video content protection and monitoring',
                    'category': TemplateCategory.VIDEOGRAPHER,
                    'template_type': TemplateType.CONTENT_PROTECTION,
                    'workflow_definition': self._create_video_protection_workflow(),
                    'tags': ['video', 'protection', 'copyright'],
                    'complexity_level': 'advanced',
                    'estimated_duration': 90
                },
                {
                    'name': 'Podcast Production Workflow',
                    'description': 'Complete podcast production from recording to distribution',
                    'category': TemplateCategory.PODCASTER,
                    'template_type': TemplateType.AUDIO_PROCESSING,
                    'workflow_definition': self._create_podcast_workflow(),
                    'tags': ['podcast', 'audio', 'production'],
                    'complexity_level': 'intermediate',
                    'estimated_duration': 60
                },
                {
                    'name': 'SEO Content Optimization',
                    'description': 'Optimize content for search engines and social media',
                    'category': TemplateCategory.BLOGGER,
                    'template_type': TemplateType.SEO_OPTIMIZATION,
                    'workflow_definition': self._create_seo_workflow(),
                    'tags': ['seo', 'content', 'optimization'],
                    'complexity_level': 'beginner',
                    'estimated_duration': 30
                }
            ]
            
            # Create built-in templates
            for template_def in builtin_templates:
                asyncio.create_task(self.create_template(**template_def))
            
        except Exception as e:
            self.logger.error(f"Error initializing builtin templates: {str(e)}")

    def _create_music_release_workflow(self) -> Dict[str, Any]:
        """Create music release workflow definition."""
        return {
            'id': 'music_release_workflow',
            'name': 'Music Release Workflow',
            'nodes': [
                {
                    'id': 'audio_processing',
                    'name': 'Audio Processing',
                    'task_type': 'audio_agent',
                    'executor': 'process_audio_track',
                    'parameters': {'quality': '{{ audio_quality }}', 'format': '{{ output_format }}'}
                },
                {
                    'id': 'fingerprinting',
                    'name': 'Audio Fingerprinting',
                    'task_type': 'fingerprinting_agent',
                    'executor': 'generate_audio_fingerprint',
                    'dependencies': ['audio_processing']
                },
                {
                    'id': 'metadata_extraction',
                    'name': 'Extract Metadata',
                    'task_type': 'music_agent',
                    'executor': 'extract_music_metadata',
                    'dependencies': ['audio_processing']
                },
                {
                    'id': 'spotify_upload',
                    'name': 'Upload to Spotify',
                    'task_type': 'spotify_agent',
                    'executor': 'upload_track',
                    'dependencies': ['fingerprinting', 'metadata_extraction']
                },
                {
                    'id': 'protection_monitoring',
                    'name': 'Start Protection Monitoring',
                    'task_type': 'protection_agent',
                    'executor': 'start_monitoring',
                    'dependencies': ['spotify_upload']
                }
            ],
            'edges': [
                {'from': 'audio_processing', 'to': 'fingerprinting'},
                {'from': 'audio_processing', 'to': 'metadata_extraction'},
                {'from': 'fingerprinting', 'to': 'spotify_upload'},
                {'from': 'metadata_extraction', 'to': 'spotify_upload'},
                {'from': 'spotify_upload', 'to': 'protection_monitoring'}
            ]
        }

    def _create_social_media_workflow(self) -> Dict[str, Any]:
        """Create social media content workflow definition."""
        return {
            'id': 'social_media_workflow',
            'name': 'Social Media Content Pipeline',
            'nodes': [
                {
                    'id': 'content_generation',
                    'name': 'Generate Content',
                    'task_type': 'content_agent',
                    'executor': 'generate_social_content',
                    'parameters': {'platforms': '{{ target_platforms }}', 'tone': '{{ brand_tone }}'}
                },
                {
                    'id': 'image_processing',
                    'name': 'Process Images',
                    'task_type': 'image_agent',
                    'executor': 'optimize_images',
                    'dependencies': ['content_generation']
                },
                {
                    'id': 'seo_optimization',
                    'name': 'SEO Optimization',
                    'task_type': 'seo_agent',
                    'executor': 'optimize_content',
                    'dependencies': ['content_generation']
                },
                {
                    'id': 'scheduling',
                    'name': 'Schedule Posts',
                    'task_type': 'scheduling_agent',
                    'executor': 'schedule_posts',
                    'dependencies': ['image_processing', 'seo_optimization']
                }
            ],
            'edges': [
                {'from': 'content_generation', 'to': 'image_processing'},
                {'from': 'content_generation', 'to': 'seo_optimization'},
                {'from': 'image_processing', 'to': 'scheduling'},
                {'from': 'seo_optimization', 'to': 'scheduling'}
            ]
        }

    def _create_video_protection_workflow(self) -> Dict[str, Any]:
        """Create video protection workflow definition."""
        return {
            'id': 'video_protection_workflow',
            'name': 'Video Content Protection',
            'nodes': [
                {
                    'id': 'video_analysis',
                    'name': 'Analyze Video',
                    'task_type': 'video_agent',
                    'executor': 'analyze_video_content',
                    'parameters': {'extract_frames': True, 'audio_analysis': True}
                },
                {
                    'id': 'fingerprint_generation',
                    'name': 'Generate Fingerprints',
                    'task_type': 'fingerprinting_agent',
                    'executor': 'generate_video_fingerprint',
                    'dependencies': ['video_analysis']
                },
                {
                    'id': 'web_monitoring',
                    'name': 'Start Web Monitoring',
                    'task_type': 'crawling_agent',
                    'executor': 'start_video_monitoring',
                    'dependencies': ['fingerprint_generation']
                },
                {
                    'id': 'dmca_setup',
                    'name': 'Setup DMCA Protection',
                    'task_type': 'dmca_agent',
                    'executor': 'setup_dmca_protection',
                    'dependencies': ['fingerprint_generation']
                }
            ],
            'edges': [
                {'from': 'video_analysis', 'to': 'fingerprint_generation'},
                {'from': 'fingerprint_generation', 'to': 'web_monitoring'},
                {'from': 'fingerprint_generation', 'to': 'dmca_setup'}
            ]
        }

    def _create_podcast_workflow(self) -> Dict[str, Any]:
        """Create podcast workflow definition."""
        return {
            'id': 'podcast_workflow',
            'name': 'Podcast Production Workflow',
            'nodes': [
                {
                    'id': 'audio_enhancement',
                    'name': 'Enhance Audio',
                    'task_type': 'audio_agent',
                    'executor': 'enhance_podcast_audio',
                    'parameters': {'noise_reduction': True, 'normalize': True}
                },
                {
                    'id': 'transcript_generation',
                    'name': 'Generate Transcript',
                    'task_type': 'nlp_agent',
                    'executor': 'generate_transcript',
                    'dependencies': ['audio_enhancement']
                },
                {
                    'id': 'show_notes',
                    'name': 'Generate Show Notes',
                    'task_type': 'content_agent',
                    'executor': 'generate_show_notes',
                    'dependencies': ['transcript_generation']
                },
                {
                    'id': 'distribution',
                    'name': 'Distribute Podcast',
                    'task_type': 'distribution_agent',
                    'executor': 'distribute_podcast',
                    'dependencies': ['show_notes']
                }
            ],
            'edges': [
                {'from': 'audio_enhancement', 'to': 'transcript_generation'},
                {'from': 'transcript_generation', 'to': 'show_notes'},
                {'from': 'show_notes', 'to': 'distribution'}
            ]
        }

    def _create_seo_workflow(self) -> Dict[str, Any]:
        """Create SEO optimization workflow definition."""
        return {
            'id': 'seo_workflow',
            'name': 'SEO Content Optimization',
            'nodes': [
                {
                    'id': 'keyword_research',
                    'name': 'Keyword Research',
                    'task_type': 'seo_agent',
                    'executor': 'research_keywords',
                    'parameters': {'target_audience': '{{ audience }}', 'industry': '{{ industry }}'}
                },
                {
                    'id': 'content_optimization',
                    'name': 'Optimize Content',
                    'task_type': 'seo_agent',
                    'executor': 'optimize_content_seo',
                    'dependencies': ['keyword_research']
                },
                {
                    'id': 'meta_generation',
                    'name': 'Generate Meta Tags',
                    'task_type': 'seo_agent',
                    'executor': 'generate_meta_tags',
                    'dependencies': ['content_optimization']
                },
                {
                    'id': 'performance_tracking',
                    'name': 'Setup Performance Tracking',
                    'task_type': 'analytics_agent',
                    'executor': 'setup_seo_tracking',
                    'dependencies': ['meta_generation']
                }
            ],
            'edges': [
                {'from': 'keyword_research', 'to': 'content_optimization'},
                {'from': 'content_optimization', 'to': 'meta_generation'},
                {'from': 'meta_generation', 'to': 'performance_tracking'}
            ]
        }

    async def _validate_workflow_definition(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow definition structure."""
        try:
            errors = []
            
            # Check required fields
            required_fields = ['nodes', 'edges']
            for field in required_fields:
                if field not in workflow_definition:
                    errors.append(f"Missing required field: {field}")
            
            # Validate nodes
            nodes = workflow_definition.get('nodes', [])
            if not isinstance(nodes, list):
                errors.append("Nodes must be a list")
            else:
                node_ids = set()
                for i, node in enumerate(nodes):
                    if not isinstance(node, dict):
                        errors.append(f"Node {i} must be a dictionary")
                        continue
                    
                    if 'id' not in node:
                        errors.append(f"Node {i} missing id field")
                    else:
                        if node['id'] in node_ids:
                            errors.append(f"Duplicate node id: {node['id']}")
                        node_ids.add(node['id'])
            
            # Validate edges
            edges = workflow_definition.get('edges', [])
            if not isinstance(edges, list):
                errors.append("Edges must be a list")
            else:
                for i, edge in enumerate(edges):
                    if not isinstance(edge, dict):
                        errors.append(f"Edge {i} must be a dictionary")
                        continue
                    
                    if 'from' not in edge or 'to' not in edge:
                        errors.append(f"Edge {i} missing 'from' or 'to' field")
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}

    async def _generate_validation_schema(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON schema for workflow validation."""
        try:
            # Basic workflow schema
            schema = {
                "type": "object",
                "properties": {
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "task_type": {"type": "string"},
                                "executor": {"type": "string"}
                            },
                            "required": ["id", "name", "task_type", "executor"]
                        }
                    },
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string"},
                                "to": {"type": "string"}
                            },
                            "required": ["from", "to"]
                        }
                    }
                },
                "required": ["nodes", "edges"]
            }
            
            return schema
            
        except Exception as e:
            self.logger.error(f"Schema generation error: {str(e)}")
            return {}

    async def _extract_template_parameters(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Extract template parameters from workflow definition."""
        try:
            parameters = {}
            
            # Convert workflow to JSON string to find template variables
            workflow_str = json.dumps(workflow_definition)
            
            # Find Jinja2 template variables
            env = Environment()
            ast = env.parse(workflow_str)
            variables = meta.find_undeclared_variables(ast)
            
            # Create parameter definitions
            for var in variables:
                parameters[var] = {
                    'type': 'string',
                    'description': f'Template parameter: {var}',
                    'required': True
                }
            
            return parameters
            
        except Exception as e:
            self.logger.warning(f"Parameter extraction error: {str(e)}")
            return {}

    async def _validate_customizations(
        self,
        template: WorkflowTemplate,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate template customizations."""
        try:
            errors = []
            
            # Check against template parameters
            for param_name, value in customizations.items():
                if param_name not in template.parameters:
                    errors.append(f"Unknown parameter: {param_name}")
                    continue
                
                param_def = template.parameters[param_name]
                
                # Type checking (basic)
                expected_type = param_def.get('type', 'string')
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Parameter {param_name} must be a string")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Parameter {param_name} must be a number")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Parameter {param_name} must be a boolean")
            
            # Check required parameters
            for param_name, param_def in template.parameters.items():
                if param_def.get('required', False) and param_name not in customizations:
                    errors.append(f"Required parameter missing: {param_name}")
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}

    async def _apply_customizations(
        self,
        workflow_definition: Dict[str, Any],
        customizations: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply customizations to workflow definition."""
        try:
            # Convert to JSON string for template rendering
            workflow_str = json.dumps(workflow_definition)
            
            # Render template with customizations
            template = self.template_env.from_string(workflow_str)
            rendered_str = template.render(**customizations)
            
            # Parse back to dictionary
            customized_workflow = json.loads(rendered_str)
            
            return customized_workflow
            
        except Exception as e:
            self.logger.error(f"Customization application error: {str(e)}")
            raise

    def _update_usage_patterns(self, template_id: str, user_id: str):
        """Update usage patterns for analytics."""
        try:
            # Update popular templates
            if template_id not in self.template_analytics['popular_templates']:
                self.template_analytics['popular_templates'][template_id] = 0
            self.template_analytics['popular_templates'][template_id] += 1
            
            # Update usage patterns
            pattern_key = f"{template_id}:{user_id}"
            if pattern_key not in self.template_analytics['usage_patterns']:
                self.template_analytics['usage_patterns'][pattern_key] = {
                    'count': 0,
                    'last_used': datetime.now()
                }
            
            self.template_analytics['usage_patterns'][pattern_key]['count'] += 1
            self.template_analytics['usage_patterns'][pattern_key]['last_used'] = datetime.now()
            
        except Exception as e:
            self.logger.warning(f"Usage pattern update error: {str(e)}")

    def _load_validation_schemas(self) -> Dict[str, Any]:
        """Load validation schemas."""
        # Placeholder - would load from files or define schemas
        return {}

    async def _save_template_to_disk(self, template: WorkflowTemplate):
        """Save template to disk."""
        try:
            template_file = self.template_directory / f"{template.metadata.id}.json"
            
            template_data = {
                'metadata': asdict(template.metadata),
                'workflow_definition': template.workflow_definition,
                'parameters': template.parameters,
                'validation_schema': template.validation_schema,
                'documentation': template.documentation,
                'examples': template.examples,
                'customization_options': template.customization_options
            }
            
            # Convert datetime objects to ISO format
            template_data['metadata']['created_at'] = template.metadata.created_at.isoformat()
            template_data['metadata']['updated_at'] = template.metadata.updated_at.isoformat()
            
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving template to disk: {str(e)}")

    async def _load_template_from_disk(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Load template from disk."""
        try:
            template_file = self.template_directory / f"{template_id}.json"
            
            if not template_file.exists():
                return None
            
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            # Convert back to objects
            metadata_data = template_data['metadata']
            metadata_data['created_at'] = datetime.fromisoformat(metadata_data['created_at'])
            metadata_data['updated_at'] = datetime.fromisoformat(metadata_data['updated_at'])
            metadata_data['category'] = TemplateCategory(metadata_data['category'])
            metadata_data['template_type'] = TemplateType(metadata_data['template_type'])
            
            metadata = TemplateMetadata(**metadata_data)
            
            template = WorkflowTemplate(
                metadata=metadata,
                workflow_definition=template_data['workflow_definition'],
                parameters=template_data['parameters'],
                validation_schema=template_data['validation_schema'],
                documentation=template_data['documentation'],
                examples=template_data['examples'],
                customization_options=template_data['customization_options']
            )
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error loading template from disk: {str(e)}")
            return None

    async def get_template_analytics(self) -> Dict[str, Any]:
        """Get template usage analytics."""
        return {
            'analytics': self.template_analytics.copy(),
            'top_templates': sorted(
                self.template_analytics['popular_templates'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

# Import asyncio at module level for the builtin template initialization
import asyncio
