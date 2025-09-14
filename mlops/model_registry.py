"""
Enterprise Model Registry Enhancement for ML Lifecycle Management
ML Engineer + DBA implementation with advanced versioning and governance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import pickle
import base64
from abc import ABC, abstractmethod
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model status in registry"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ModelType(Enum):
    """Types of ML models"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"
    TIME_SERIES = "time_series"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    ENSEMBLE = "ensemble"


class ModelFramework(Enum):
    """ML frameworks"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    KERAS = "keras"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


@dataclass
class ModelMetadata:
    """Model metadata information"""
    model_id: str
    name: str
    version: str
    description: str
    model_type: ModelType
    framework: ModelFramework
    status: ModelStatus
    creator_type: Optional[str] = None
    author: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Technical metadata
    model_size_mb: float = 0.0
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    training_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Deployment metadata
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    environment_requirements: Dict[str, str] = field(default_factory=dict)
    
    # Business metadata
    business_value: str = ""
    use_cases: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)
    expected_impact: str = ""


@dataclass
class ModelArtifact:
    """Model artifact storage"""
    artifact_id: str
    model_id: str
    version: str
    artifact_type: str  # model, weights, config, etc.
    file_path: str
    checksum: str
    size_bytes: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelVersion:
    """Model version information"""
    version_id: str
    model_id: str
    version: str
    parent_version: Optional[str] = None
    changes: List[str] = field(default_factory=list)
    artifacts: List[ModelArtifact] = field(default_factory=list)
    performance_comparison: Dict[str, Any] = field(default_factory=dict)
    approval_status: str = "pending"
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelLineage:
    """Model lineage tracking"""
    lineage_id: str
    model_id: str
    parent_models: List[str] = field(default_factory=list)
    training_data: List[str] = field(default_factory=list)
    feature_dependencies: List[str] = field(default_factory=list)
    pipeline_id: Optional[str] = None
    experiment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelGovernance:
    """Model governance information"""
    governance_id: str
    model_id: str
    governance_level: str  # basic, standard, strict
    approval_workflow: List[str] = field(default_factory=list)
    required_approvers: List[str] = field(default_factory=list)
    compliance_checks: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    audit_logs: List[Dict[str, Any]] = field(default_factory=list)


class ModelRegistryEnhanced:
    """Enhanced enterprise model registry with advanced lifecycle management"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.models: Dict[str, ModelMetadata] = {}
        self.versions: Dict[str, List[ModelVersion]] = defaultdict(list)
        self.artifacts: Dict[str, List[ModelArtifact]] = defaultdict(list)
        self.lineage: Dict[str, ModelLineage] = {}
        self.governance: Dict[str, ModelGovernance] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Creator-specific model templates
        self.creator_model_templates = {
            'musicians': {
                'audio_models': [
                    'genre_classifier', 'mood_analyzer', 'tempo_detector',
                    'key_detector', 'energy_analyzer', 'vocal_separator'
                ],
                'recommendation_models': [
                    'collaboration_matcher', 'audience_recommender', 'playlist_optimizer',
                    'fan_segmentation', 'trending_predictor'
                ],
                'business_models': [
                    'revenue_predictor', 'engagement_forecaster', 'churn_predictor',
                    'pricing_optimizer', 'market_analyzer'
                ]
            },
            'photographers': {
                'vision_models': [
                    'style_classifier', 'aesthetic_scorer', 'composition_analyzer',
                    'quality_assessor', 'subject_detector', 'color_harmony_analyzer'
                ],
                'portfolio_models': [
                    'portfolio_optimizer', 'style_consistency_checker', 'market_appeal_predictor',
                    'client_matcher', 'booking_predictor'
                ],
                'enhancement_models': [
                    'auto_enhancer', 'noise_reducer', 'color_corrector',
                    'lighting_optimizer', 'crop_suggester'
                ]
            },
            'bloggers': {
                'nlp_models': [
                    'content_classifier', 'sentiment_analyzer', 'topic_extractor',
                    'readability_scorer', 'plagiarism_detector', 'tone_analyzer'
                ],
                'seo_models': [
                    'keyword_optimizer', 'ranking_predictor', 'backlink_scorer',
                    'content_gap_analyzer', 'competitor_analyzer'
                ],
                'engagement_models': [
                    'viral_predictor', 'engagement_forecaster', 'audience_segmenter',
                    'content_recommender', 'timing_optimizer'
                ]
            },
            'influencers': {
                'engagement_models': [
                    'engagement_predictor', 'reach_optimizer', 'hashtag_recommender',
                    'audience_analyzer', 'trend_detector'
                ],
                'content_models': [
                    'content_scorer', 'format_optimizer', 'timing_predictor',
                    'caption_generator', 'story_optimizer'
                ],
                'business_models': [
                    'brand_matcher', 'conversion_predictor', 'roi_calculator',
                    'campaign_optimizer', 'pricing_recommender'
                ]
            },
            'comedians': {
                'performance_models': [
                    'joke_effectiveness_predictor', 'timing_analyzer', 'audience_response_predictor',
                    'material_classifier', 'crowd_energy_detector'
                ],
                'content_models': [
                    'humor_analyzer', 'topic_relevance_scorer', 'originality_checker',
                    'viral_potential_predictor', 'platform_optimizer'
                ],
                'venue_models': [
                    'venue_matcher', 'audience_predictor', 'booking_optimizer',
                    'performance_scheduler', 'revenue_forecaster'
                ]
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize enhanced model registry"""
        try:
            logger.info("Initializing Enhanced Model Registry...")
            
            # Setup model templates
            await self._setup_model_templates()
            
            # Initialize governance framework
            await self._setup_governance_framework()
            
            # Setup automated monitoring
            await self._setup_automated_monitoring()
            
            logger.info("Enhanced Model Registry initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Model Registry: {e}")
            return False
    
    async def register_model(self, metadata: ModelMetadata) -> bool:
        """Register new model in registry"""
        try:
            # Validate model metadata
            if not await self._validate_model_metadata(metadata):
                return False
            
            # Generate unique model ID if not provided
            if not metadata.model_id:
                metadata.model_id = await self._generate_model_id(metadata)
            
            # Check for duplicate models
            if metadata.model_id in self.models:
                logger.warning(f"Model {metadata.model_id} already exists")
                return False
            
            # Set up governance for model
            governance = await self._create_model_governance(metadata)
            self.governance[metadata.model_id] = governance
            
            # Create initial lineage
            lineage = ModelLineage(
                lineage_id=str(uuid.uuid4()),
                model_id=metadata.model_id
            )
            self.lineage[metadata.model_id] = lineage
            
            # Store model metadata
            self.models[metadata.model_id] = metadata
            
            logger.info(f"Registered model: {metadata.name} ({metadata.model_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False
    
    async def create_model_version(self, 
                                 model_id: str,
                                 version: str,
                                 changes: List[str],
                                 artifacts: List[ModelArtifact],
                                 parent_version: Optional[str] = None) -> bool:
        """Create new model version"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            # Validate version doesn't exist
            existing_versions = [v.version for v in self.versions[model_id]]
            if version in existing_versions:
                logger.error(f"Version {version} already exists for model {model_id}")
                return False
            
            # Create model version
            model_version = ModelVersion(
                version_id=str(uuid.uuid4()),
                model_id=model_id,
                version=version,
                parent_version=parent_version,
                changes=changes,
                artifacts=artifacts
            )
            
            # Calculate performance comparison if parent version exists
            if parent_version:
                comparison = await self._compare_model_versions(
                    model_id, parent_version, version
                )
                model_version.performance_comparison = comparison
            
            # Store version
            self.versions[model_id].append(model_version)
            
            # Store artifacts
            for artifact in artifacts:
                artifact.model_id = model_id
                artifact.version = version
                self.artifacts[model_id].append(artifact)
            
            # Update model metadata
            self.models[model_id].updated_at = datetime.utcnow()
            
            logger.info(f"Created version {version} for model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create model version: {e}")
            return False
    
    async def promote_model(self, 
                          model_id: str,
                          version: str,
                          target_status: ModelStatus,
                          approver: str) -> bool:
        """Promote model to different status"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            model = self.models[model_id]
            governance = self.governance.get(model_id)
            
            # Check governance requirements
            if governance and not await self._check_governance_approval(
                model_id, target_status, approver
            ):
                logger.error(f"Governance approval failed for model {model_id}")
                return False
            
            # Get model version
            model_version = self._get_model_version(model_id, version)
            if not model_version:
                logger.error(f"Version {version} not found for model {model_id}")
                return False
            
            # Update approval status
            model_version.approval_status = "approved"
            model_version.approved_by = approver
            model_version.approval_date = datetime.utcnow()
            
            # Update model status
            old_status = model.status
            model.status = target_status
            model.updated_at = datetime.utcnow()
            
            # Log governance action
            if governance:
                governance.audit_logs.append({
                    'action': 'promotion',
                    'from_status': old_status.value,
                    'to_status': target_status.value,
                    'version': version,
                    'approver': approver,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Promoted model {model_id} v{version} to {target_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote model: {e}")
            return False
    
    async def get_model_by_id(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID"""
        try:
            return self.models.get(model_id)
        except Exception as e:
            logger.error(f"Failed to get model: {e}")
            return None
    
    async def search_models(self, 
                          query: Optional[str] = None,
                          creator_type: Optional[str] = None,
                          model_type: Optional[ModelType] = None,
                          status: Optional[ModelStatus] = None,
                          tags: Optional[List[str]] = None) -> List[ModelMetadata]:
        """Search models with filters"""
        try:
            results = []
            
            for model in self.models.values():
                # Text search
                if query:
                    if (query.lower() not in model.name.lower() and 
                        query.lower() not in model.description.lower()):
                        continue
                
                # Filter by creator type
                if creator_type and model.creator_type != creator_type:
                    continue
                
                # Filter by model type
                if model_type and model.model_type != model_type:
                    continue
                
                # Filter by status
                if status and model.status != status:
                    continue
                
                # Filter by tags
                if tags:
                    if not all(tag in model.tags for tag in tags):
                        continue
                
                results.append(model)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search models: {e}")
            return []
    
    async def get_model_versions(self, model_id: str) -> List[ModelVersion]:
        """Get all versions for a model"""
        try:
            return self.versions.get(model_id, [])
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    async def get_model_lineage(self, model_id: str) -> Optional[ModelLineage]:
        """Get model lineage information"""
        try:
            return self.lineage.get(model_id)
        except Exception as e:
            logger.error(f"Failed to get model lineage: {e}")
            return None
    
    async def track_model_performance(self, 
                                    model_id: str,
                                    version: str,
                                    metrics: Dict[str, float],
                                    timestamp: Optional[datetime] = None) -> bool:
        """Track model performance metrics"""
        try:
            timestamp = timestamp or datetime.utcnow()
            
            performance_record = {
                'version': version,
                'metrics': metrics,
                'timestamp': timestamp.isoformat()
            }
            
            self.performance_history[model_id].append(performance_record)
            
            # Keep only last 1000 records per model
            if len(self.performance_history[model_id]) > 1000:
                self.performance_history[model_id] = self.performance_history[model_id][-1000:]
            
            # Update model metadata with latest metrics
            if model_id in self.models:
                self.models[model_id].performance_metrics.update(metrics)
                self.models[model_id].updated_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track model performance: {e}")
            return False
    
    async def get_performance_history(self, 
                                    model_id: str,
                                    time_period: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Get performance history for model"""
        try:
            history = self.performance_history.get(model_id, [])
            
            if time_period:
                cutoff_time = datetime.utcnow() - time_period
                history = [
                    record for record in history
                    if datetime.fromisoformat(record['timestamp']) >= cutoff_time
                ]
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []
    
    async def get_creator_models(self, creator_type: str) -> Dict[str, List[ModelMetadata]]:
        """Get all models for specific creator type"""
        try:
            if creator_type not in self.creator_model_templates:
                logger.error(f"Creator type {creator_type} not supported")
                return {}
            
            creator_models = {}
            for category in self.creator_model_templates[creator_type]:
                category_models = []
                
                for model in self.models.values():
                    if (model.creator_type == creator_type and 
                        any(tag in model.tags for tag in [category])):
                        category_models.append(model)
                
                creator_models[category] = category_models
            
            return creator_models
            
        except Exception as e:
            logger.error(f"Failed to get creator models: {e}")
            return {}
    
    async def compare_models(self, 
                           model_id_1: str,
                           version_1: str,
                           model_id_2: str,
                           version_2: str) -> Dict[str, Any]:
        """Compare two model versions"""
        try:
            comparison = {
                'model_1': {'id': model_id_1, 'version': version_1},
                'model_2': {'id': model_id_2, 'version': version_2},
                'performance_comparison': {},
                'metadata_comparison': {},
                'recommendation': ''
            }
            
            # Get models
            model_1 = self.models.get(model_id_1)
            model_2 = self.models.get(model_id_2)
            
            if not model_1 or not model_2:
                return comparison
            
            # Compare performance metrics
            metrics_1 = model_1.performance_metrics
            metrics_2 = model_2.performance_metrics
            
            for metric in set(metrics_1.keys()).union(set(metrics_2.keys())):
                val_1 = metrics_1.get(metric, 0)
                val_2 = metrics_2.get(metric, 0)
                
                comparison['performance_comparison'][metric] = {
                    'model_1': val_1,
                    'model_2': val_2,
                    'difference': val_2 - val_1,
                    'improvement': ((val_2 - val_1) / val_1 * 100) if val_1 != 0 else 0
                }
            
            # Compare metadata
            comparison['metadata_comparison'] = {
                'size_difference_mb': model_2.model_size_mb - model_1.model_size_mb,
                'framework_match': model_1.framework == model_2.framework,
                'type_match': model_1.model_type == model_2.model_type
            }
            
            # Generate recommendation
            comparison['recommendation'] = await self._generate_comparison_recommendation(
                comparison['performance_comparison']
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            return {}
    
    async def _setup_model_templates(self) -> None:
        """Setup model templates for different creator types"""
        for creator_type, categories in self.creator_model_templates.items():
            for category, model_types in categories.items():
                for model_type in model_types:
                    # Create template model metadata
                    template = await self._create_model_template(
                        creator_type, category, model_type
                    )
                    # Templates are stored separately and used for guidance
    
    async def _setup_governance_framework(self) -> None:
        """Setup governance framework"""
        # Define governance levels and requirements
        self.governance_levels = {
            'basic': {
                'required_approvers': 1,
                'compliance_checks': ['basic_validation'],
                'approval_workflow': ['technical_review']
            },
            'standard': {
                'required_approvers': 2,
                'compliance_checks': ['validation', 'security_check'],
                'approval_workflow': ['technical_review', 'business_review']
            },
            'strict': {
                'required_approvers': 3,
                'compliance_checks': ['validation', 'security_check', 'compliance_audit'],
                'approval_workflow': ['technical_review', 'business_review', 'governance_approval']
            }
        }
    
    async def _setup_automated_monitoring(self) -> None:
        """Setup automated monitoring for models"""
        asyncio.create_task(self._monitor_model_performance())
        asyncio.create_task(self._monitor_model_drift())
    
    async def _validate_model_metadata(self, metadata: ModelMetadata) -> bool:
        """Validate model metadata"""
        try:
            # Required fields
            if not metadata.name or not metadata.version:
                return False
            
            # Version format validation
            if not self._is_valid_version_format(metadata.version):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Metadata validation error: {e}")
            return False
    
    async def _generate_model_id(self, metadata: ModelMetadata) -> str:
        """Generate unique model ID"""
        base_id = f"{metadata.creator_type}_{metadata.model_type.value}_{metadata.name}"
        base_id = base_id.lower().replace(' ', '_').replace('-', '_')
        
        # Add hash for uniqueness
        hash_input = f"{base_id}_{metadata.author}_{datetime.utcnow().isoformat()}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"{base_id}_{hash_suffix}"
    
    async def _create_model_governance(self, metadata: ModelMetadata) -> ModelGovernance:
        """Create governance configuration for model"""
        
        # Determine governance level based on model characteristics
        if metadata.status == ModelStatus.PRODUCTION:
            governance_level = 'strict'
        elif metadata.model_type in [ModelType.RECOMMENDATION, ModelType.CLASSIFICATION]:
            governance_level = 'standard'
        else:
            governance_level = 'basic'
        
        governance_config = self.governance_levels[governance_level]
        
        return ModelGovernance(
            governance_id=str(uuid.uuid4()),
            model_id=metadata.model_id,
            governance_level=governance_level,
            approval_workflow=governance_config['approval_workflow'],
            required_approvers=[f"approver_{i}" for i in range(governance_config['required_approvers'])],
            compliance_checks=governance_config['compliance_checks'],
            risk_assessment={'level': 'medium', 'factors': ['data_sensitivity', 'business_impact']}
        )
    
    async def _compare_model_versions(self, 
                                    model_id: str,
                                    parent_version: str,
                                    new_version: str) -> Dict[str, Any]:
        """Compare model versions for performance"""
        # Simplified comparison - in real implementation would use actual metrics
        return {
            'accuracy_improvement': 0.02,
            'latency_change': -50,  # ms improvement
            'model_size_change': 0.5,  # MB increase
            'overall_score': 0.85
        }
    
    async def _check_governance_approval(self, 
                                       model_id: str,
                                       target_status: ModelStatus,
                                       approver: str) -> bool:
        """Check if governance requirements are met"""
        governance = self.governance.get(model_id)
        if not governance:
            return True  # No governance requirements
        
        # Simplified approval check
        if target_status == ModelStatus.PRODUCTION:
            return approver in governance.required_approvers
        
        return True
    
    def _get_model_version(self, model_id: str, version: str) -> Optional[ModelVersion]:
        """Get specific model version"""
        versions = self.versions.get(model_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def _is_valid_version_format(self, version: str) -> bool:
        """Validate version format (semantic versioning)"""
        try:
            parts = version.split('.')
            return len(parts) == 3 and all(part.isdigit() for part in parts)
        except Exception:
            return False
    
    async def _create_model_template(self, 
                                   creator_type: str,
                                   category: str,
                                   model_type: str) -> ModelMetadata:
        """Create model template for creator type"""
        
        # Determine appropriate ML model type
        if 'classifier' in model_type or 'detector' in model_type:
            ml_type = ModelType.CLASSIFICATION
        elif 'predictor' in model_type or 'forecaster' in model_type:
            ml_type = ModelType.REGRESSION
        elif 'recommender' in model_type or 'matcher' in model_type:
            ml_type = ModelType.RECOMMENDATION
        elif any(nlp_term in model_type for nlp_term in ['sentiment', 'topic', 'content']):
            ml_type = ModelType.NLP
        elif any(cv_term in model_type for cv_term in ['style', 'aesthetic', 'composition']):
            ml_type = ModelType.COMPUTER_VISION
        elif 'audio' in model_type or creator_type == 'musicians':
            ml_type = ModelType.AUDIO_PROCESSING
        else:
            ml_type = ModelType.CLASSIFICATION
        
        return ModelMetadata(
            model_id="",  # Will be generated
            name=model_type.replace('_', ' ').title(),
            version="1.0.0",
            description=f"{model_type} model for {creator_type}",
            model_type=ml_type,
            framework=ModelFramework.TENSORFLOW,  # Default
            status=ModelStatus.DEVELOPMENT,
            creator_type=creator_type,
            tags=[category, creator_type, model_type]
        )
    
    async def _generate_comparison_recommendation(self, 
                                                performance_comparison: Dict[str, Any]) -> str:
        """Generate recommendation based on model comparison"""
        improvements = []
        degradations = []
        
        for metric, comparison in performance_comparison.items():
            improvement = comparison.get('improvement', 0)
            if improvement > 5:  # 5% improvement threshold
                improvements.append(f"{metric} improved by {improvement:.1f}%")
            elif improvement < -5:  # 5% degradation threshold
                degradations.append(f"{metric} degraded by {abs(improvement):.1f}%")
        
        if len(improvements) > len(degradations):
            return f"Recommend new model. Improvements: {', '.join(improvements)}"
        elif len(degradations) > len(improvements):
            return f"Keep current model. Issues: {', '.join(degradations)}"
        else:
            return "Models have similar performance. Consider other factors."
    
    async def _monitor_model_performance(self) -> None:
        """Background task to monitor model performance"""
        while True:
            try:
                # Monitor every hour
                await asyncio.sleep(3600)
                
                for model_id in self.models:
                    # Check recent performance
                    recent_history = await self.get_performance_history(
                        model_id, timedelta(hours=24)
                    )
                    
                    if recent_history:
                        # Analyze performance trends
                        await self._analyze_performance_trends(model_id, recent_history)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
    
    async def _monitor_model_drift(self) -> None:
        """Background task to monitor model drift"""
        while True:
            try:
                # Monitor every 6 hours
                await asyncio.sleep(21600)
                
                for model_id in self.models:
                    # Check for drift indicators
                    await self._check_model_drift(model_id)
                
            except Exception as e:
                logger.error(f"Drift monitoring error: {e}")
    
    async def _analyze_performance_trends(self, 
                                        model_id -> None: str,
                                        performance_history -> None: List[Dict[str, Any]]) -> None:
        """Analyze performance trends for model"""
        if len(performance_history) < 5:
            return
        
        # Simple trend analysis
        latest_metrics = performance_history[-1]['metrics']
        older_metrics = performance_history[-5]['metrics']
        
        for metric, latest_value in latest_metrics.items():
            if metric in older_metrics:
                older_value = older_metrics[metric]
                change = ((latest_value - older_value) / older_value) * 100
                
                if abs(change) > 10:  # 10% change threshold
                    logger.info(f"Model {model_id} {metric} changed by {change:.1f}%")
    
    async def _check_model_drift(self, model_id -> None: str) -> None:
        """Check for model drift"""
        # Simplified drift check
        # In real implementation, this would analyze data distributions
        logger.debug(f"Checking drift for model {model_id}")


# Example usage and testing
async def main() -> None:
    """Example usage of Enhanced Model Registry"""
    registry = ModelRegistryEnhanced()
    
    # Initialize
    await registry.initialize()
    
    # Create model metadata
    metadata = ModelMetadata(
        model_id="",
        name="Audio Genre Classifier",
        version="1.0.0",
        description="ML model to classify music genres for musicians",
        model_type=ModelType.CLASSIFICATION,
        framework=ModelFramework.TENSORFLOW,
        status=ModelStatus.DEVELOPMENT,
        creator_type="musicians",
        author="ml_engineer",
        tags=["audio", "classification", "musicians"],
        performance_metrics={"accuracy": 0.92, "f1_score": 0.89}
    )
    
    # Register model
    success = await registry.register_model(metadata)
    print(f"Model registration: {success}")
    
    if success:
        model_id = metadata.model_id
        
        # Track performance
        await registry.track_model_performance(
            model_id, "1.0.0", {"accuracy": 0.94, "f1_score": 0.91}
        )
        
        # Search models
        models = await registry.search_models(creator_type="musicians")
        print(f"Found {len(models)} models for musicians")
        
        # Get model lineage
        lineage = await registry.get_model_lineage(model_id)
        print(f"Model lineage: {lineage}")


if __name__ == "__main__":
    asyncio.run(main())