"""
🔍 Data Lineage Tracker - Enterprise DBA & ML Engineering
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Traçabilité complète données Creator Economy avec governance
Expertise: DBA + ML Engineer + Backend Senior + Sécurité
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
from pathlib import Path
import networkx as nx
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources"""
    USER_GENERATED = "user_generated"
    CREATOR_CONTENT = "creator_content"
    PLATFORM_METRICS = "platform_metrics"
    EXTERNAL_API = "external_api"
    DATABASE_TABLE = "database_table"
    FILE_SYSTEM = "file_system"
    STREAM = "stream"
    SYNTHETIC = "synthetic"
    AUGMENTED = "augmented"


class ProcessingType(Enum):
    """Types of data processing operations"""
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    FEATURE_ENGINEERING = "feature_engineering"
    VALIDATION = "validation"
    CLEANSING = "cleansing"
    ANONYMIZATION = "anonymization"
    AUGMENTATION = "augmentation"
    MODEL_TRAINING = "model_training"
    MODEL_INFERENCE = "model_inference"


class DataClassification(Enum):
    """Data classification levels for Creator Economy"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CREATOR_PERSONAL = "creator_personal"
    CREATOR_CONTENT = "creator_content"
    CREATOR_ANALYTICS = "creator_analytics"
    PLATFORM_CONFIDENTIAL = "platform_confidential"
    MONETIZATION_DATA = "monetization_data"
    RESTRICTED = "restricted"


class LineageEvent(Enum):
    """Types of lineage events"""
    DATA_CREATED = "data_created"
    DATA_READ = "data_read"
    DATA_TRANSFORMED = "data_transformed"
    DATA_WRITTEN = "data_written"
    DATA_DELETED = "data_deleted"
    DATA_ARCHIVED = "data_archived"
    SCHEMA_CHANGED = "schema_changed"
    PRIVACY_APPLIED = "privacy_applied"
    QUALITY_CHECK = "quality_check"


@dataclass
class DataAsset:
    """Individual data asset"""
    asset_id: str
    name: str
    source_type: DataSourceType
    classification: DataClassification
    schema: Dict[str, Any]
    location: str
    size_bytes: int
    record_count: int
    created_at: datetime
    updated_at: datetime
    owner: str
    creator_context: Optional[Dict[str, Any]] = None
    privacy_tags: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    retention_policy: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary"""
        return {
            "asset_id": self.asset_id,
            "name": self.name,
            "source_type": self.source_type.value,
            "classification": self.classification.value,
            "schema": self.schema,
            "location": self.location,
            "size_bytes": self.size_bytes,
            "record_count": self.record_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner": self.owner,
            "creator_context": self.creator_context,
            "privacy_tags": self.privacy_tags,
            "quality_metrics": self.quality_metrics,
            "retention_policy": self.retention_policy
        }


@dataclass
class ProcessingStep:
    """Data processing step"""
    step_id: str
    name: str
    processing_type: ProcessingType
    processor: str  # System or user performing the step
    inputs: List[str]  # Input asset IDs
    outputs: List[str]  # Output asset IDs
    parameters: Dict[str, Any]
    executed_at: datetime
    execution_time_seconds: float
    status: str = "completed"  # pending, running, completed, failed
    creator_context: Optional[Dict[str, Any]] = None
    privacy_impact: Optional[Dict[str, Any]] = None
    quality_impact: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "processing_type": self.processing_type.value,
            "processor": self.processor,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
            "executed_at": self.executed_at.isoformat(),
            "execution_time_seconds": self.execution_time_seconds,
            "status": self.status,
            "creator_context": self.creator_context,
            "privacy_impact": self.privacy_impact,
            "quality_impact": self.quality_impact
        }


@dataclass
class LineageRecord:
    """Complete lineage record"""
    lineage_id: str
    root_asset_id: str
    target_asset_id: str
    processing_chain: List[ProcessingStep]
    created_at: datetime
    creator_context: Optional[Dict[str, Any]] = None
    privacy_lineage: Dict[str, Any] = field(default_factory=dict)
    quality_lineage: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lineage to dictionary"""
        return {
            "lineage_id": self.lineage_id,
            "root_asset_id": self.root_asset_id,
            "target_asset_id": self.target_asset_id,
            "processing_chain": [step.to_dict() for step in self.processing_chain],
            "created_at": self.created_at.isoformat(),
            "creator_context": self.creator_context,
            "privacy_lineage": self.privacy_lineage,
            "quality_lineage": self.quality_lineage,
            "business_context": self.business_context
        }


@dataclass
class ImpactAnalysis:
    """Data impact analysis result"""
    analysis_id: str
    asset_id: str
    downstream_count: int
    upstream_count: int
    affected_creators: List[str]
    affected_models: List[str]
    privacy_impact: str  # none, low, medium, high, critical
    business_impact: str  # none, low, medium, high, critical
    recommendations: List[str]
    analysis_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "asset_id": self.asset_id,
            "downstream_count": self.downstream_count,
            "upstream_count": self.upstream_count,
            "affected_creators": self.affected_creators,
            "affected_models": self.affected_models,
            "privacy_impact": self.privacy_impact,
            "business_impact": self.business_impact,
            "recommendations": self.recommendations,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }


class DataLineageTracker:
    """
    🔍 Traçabilité complète données Creator Economy
    
    Enterprise data lineage tracking with:
    - Source data tracking complet multi-plateforme
    - Transformation pipeline visibility temps réel
    - Creator data origin mapping avec RBAC
    - Privacy impact assessment automatisé
    - Data quality lineage tracking business metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize data lineage tracker
        
        Args:
            config: Lineage tracker configuration
        """
        self.config = config or self._get_default_config()
        self.tracker_id = str(uuid.uuid4())
        
        # Data storage
        self._data_assets: Dict[str, DataAsset] = {}
        self._processing_steps: Dict[str, ProcessingStep] = {}
        self._lineage_records: Dict[str, LineageRecord] = {}
        
        # Lineage graph (NetworkX for graph operations)
        self._lineage_graph = nx.DiGraph()
        
        # Indexing for fast lookups
        self._assets_by_creator: Dict[str, Set[str]] = defaultdict(set)
        self._assets_by_classification: Dict[DataClassification, Set[str]] = defaultdict(set)
        self._lineage_by_asset: Dict[str, Set[str]] = defaultdict(set)
        
        # Event tracking
        self._lineage_events: deque = deque(maxlen=100000)
        
        # Privacy and quality tracking
        self._privacy_lineage: Dict[str, Dict[str, Any]] = {}
        self._quality_lineage: Dict[str, Dict[str, Any]] = {}
        
        # Performance metrics
        self._tracker_metrics = {
            "assets_tracked": 0,
            "processing_steps": 0,
            "lineage_records": 0,
            "privacy_assessments": 0,
            "quality_checks": 0,
            "impact_analyses": 0
        }
        
        # Creator Economy specific tracking
        self._creator_data_mapping: Dict[str, Dict[str, Any]] = {}
        self._monetization_lineage: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"🔍 DataLineageTracker initialized with ID: {self.tracker_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default lineage tracker configuration"""
        return {
            "tracking": {
                "auto_discovery": True,
                "real_time_processing": True,
                "batch_processing": True,
                "retention_days": 365
            },
            "creator_economy": {
                "creator_data_mapping": True,
                "content_lineage": True,
                "monetization_tracking": True,
                "tier_based_access": True
            },
            "privacy": {
                "impact_assessment": True,
                "gdpr_compliance": True,
                "ccpa_compliance": True,
                "anonymization_tracking": True
            },
            "quality": {
                "quality_metrics": True,
                "drift_detection": True,
                "anomaly_detection": True,
                "data_profiling": True
            },
            "graph_analysis": {
                "enabled": True,
                "max_depth": 10,
                "cycle_detection": True,
                "impact_analysis": True
            },
            "alerts": {
                "privacy_violations": True,
                "quality_degradation": True,
                "lineage_breaks": True,
                "unauthorized_access": True
            }
        }
    
    async def register_data_asset(self, asset: DataAsset) -> bool:
        """Register a new data asset"""
        try:
            # Store asset
            self._data_assets[asset.asset_id] = asset
            
            # Update indexes
            if asset.creator_context and "creator_id" in asset.creator_context:
                creator_id = asset.creator_context["creator_id"]
                self._assets_by_creator[creator_id].add(asset.asset_id)
                
                # Update creator data mapping
                if creator_id not in self._creator_data_mapping:
                    self._creator_data_mapping[creator_id] = {
                        "assets": [],
                        "total_size": 0,
                        "classifications": set(),
                        "privacy_level": "unknown"
                    }
                
                creator_mapping = self._creator_data_mapping[creator_id]
                creator_mapping["assets"].append(asset.asset_id)
                creator_mapping["total_size"] += asset.size_bytes
                creator_mapping["classifications"].add(asset.classification.value)
            
            self._assets_by_classification[asset.classification].add(asset.asset_id)
            
            # Add to lineage graph
            self._lineage_graph.add_node(asset.asset_id, **asset.to_dict())
            
            # Initialize privacy and quality tracking
            await self._initialize_asset_tracking(asset)
            
            # Log event
            await self._log_lineage_event(
                LineageEvent.DATA_CREATED,
                asset.asset_id,
                {"asset": asset.to_dict()}
            )
            
            self._tracker_metrics["assets_tracked"] += 1
            
            logger.info(f"📊 Registered data asset: {asset.name} ({asset.asset_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register data asset: {str(e)}")
            return False
    
    async def _initialize_asset_tracking(self, asset: DataAsset) -> None:
        """Initialize privacy and quality tracking for asset"""
        try:
            # Privacy tracking initialization
            privacy_level = self._assess_privacy_level(asset)
            self._privacy_lineage[asset.asset_id] = {
                "classification": asset.classification.value,
                "privacy_level": privacy_level,
                "privacy_tags": asset.privacy_tags,
                "gdpr_applicable": "personal_data" in asset.privacy_tags,
                "ccpa_applicable": "california_resident" in asset.privacy_tags,
                "creator_consent": asset.creator_context.get("consent_status") if asset.creator_context else None,
                "anonymization_applied": "anonymized" in asset.privacy_tags
            }
            
            # Quality tracking initialization
            self._quality_lineage[asset.asset_id] = {
                "initial_quality": asset.quality_metrics,
                "quality_history": [{"timestamp": datetime.now().isoformat(), "metrics": asset.quality_metrics}],
                "quality_issues": [],
                "data_profiling": await self._profile_data_asset(asset)
            }
            
        except Exception as e:
            logger.error(f"❌ Asset tracking initialization error: {str(e)}")
    
    def _assess_privacy_level(self, asset: DataAsset) -> str:
        """Assess privacy level for an asset"""
        if asset.classification in [DataClassification.CREATOR_PERSONAL, DataClassification.MONETIZATION_DATA]:
            return "high"
        elif asset.classification in [DataClassification.CREATOR_CONTENT, DataClassification.CREATOR_ANALYTICS]:
            return "medium"
        elif asset.classification == DataClassification.PLATFORM_CONFIDENTIAL:
            return "medium"
        elif asset.classification == DataClassification.RESTRICTED:
            return "critical"
        else:
            return "low"
    
    async def _profile_data_asset(self, asset: DataAsset) -> Dict[str, Any]:
        """Profile data asset for quality metrics"""
        try:
            # Basic profiling (would integrate with actual data profiling tools)
            profile = {
                "schema_fields": len(asset.schema.get("fields", [])),
                "estimated_completeness": 0.95,  # Would calculate from actual data
                "estimated_uniqueness": 0.98,
                "estimated_validity": 0.99,
                "data_types": list(asset.schema.get("fields", {}).keys()),
                "profiling_timestamp": datetime.now().isoformat()
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Data profiling error: {str(e)}")
            return {}
    
    async def record_processing_step(self, step: ProcessingStep) -> bool:
        """Record a data processing step"""
        try:
            # Store processing step
            self._processing_steps[step.step_id] = step
            
            # Update lineage graph
            for input_id in step.inputs:
                for output_id in step.outputs:
                    # Add edge from input to output through processing step
                    self._lineage_graph.add_edge(
                        input_id, 
                        output_id,
                        step_id=step.step_id,
                        processing_type=step.processing_type.value,
                        processor=step.processor,
                        executed_at=step.executed_at.isoformat()
                    )
            
            # Update lineage indexes
            for input_id in step.inputs:
                for output_id in step.outputs:
                    self._lineage_by_asset[input_id].add(output_id)
                    self._lineage_by_asset[output_id].add(input_id)
            
            # Track privacy impact
            if step.privacy_impact:
                await self._track_privacy_impact(step)
            
            # Track quality impact
            if step.quality_impact:
                await self._track_quality_impact(step)
            
            # Creator Economy specific tracking
            if step.creator_context:
                await self._track_creator_processing(step)
            
            # Log event
            await self._log_lineage_event(
                LineageEvent.DATA_TRANSFORMED,
                step.step_id,
                {"step": step.to_dict()}
            )
            
            self._tracker_metrics["processing_steps"] += 1
            
            logger.info(f"🔄 Recorded processing step: {step.name} ({step.step_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record processing step: {str(e)}")
            return False
    
    async def _track_privacy_impact(self, step: ProcessingStep) -> None:
        """Track privacy impact of processing step"""
        try:
            for input_id in step.inputs:
                if input_id in self._privacy_lineage:
                    privacy_data = self._privacy_lineage[input_id]
                    
                    # Update privacy lineage based on processing type
                    if step.processing_type == ProcessingType.ANONYMIZATION:
                        privacy_data["anonymization_applied"] = True
                        privacy_data["privacy_level"] = "low"
                    elif step.processing_type == ProcessingType.AGGREGATION:
                        privacy_data["aggregation_applied"] = True
                    
                    # Propagate privacy concerns to outputs
                    for output_id in step.outputs:
                        if output_id not in self._privacy_lineage:
                            self._privacy_lineage[output_id] = privacy_data.copy()
                        
                        # Update with step-specific impacts
                        self._privacy_lineage[output_id].update(step.privacy_impact or {})
            
            self._tracker_metrics["privacy_assessments"] += 1
            
        except Exception as e:
            logger.error(f"❌ Privacy impact tracking error: {str(e)}")
    
    async def _track_quality_impact(self, step: ProcessingStep) -> None:
        """Track quality impact of processing step"""
        try:
            for input_id in step.inputs:
                if input_id in self._quality_lineage:
                    quality_data = self._quality_lineage[input_id]
                    
                    # Propagate quality lineage to outputs
                    for output_id in step.outputs:
                        if output_id not in self._quality_lineage:
                            self._quality_lineage[output_id] = {
                                "inherited_from": input_id,
                                "quality_history": [],
                                "quality_issues": [],
                                "transformations": []
                            }
                        
                        # Record transformation impact
                        self._quality_lineage[output_id]["transformations"].append({
                            "step_id": step.step_id,
                            "processing_type": step.processing_type.value,
                            "quality_impact": step.quality_impact,
                            "timestamp": step.executed_at.isoformat()
                        })
            
            self._tracker_metrics["quality_checks"] += 1
            
        except Exception as e:
            logger.error(f"❌ Quality impact tracking error: {str(e)}")
    
    async def _track_creator_processing(self, step: ProcessingStep) -> None:
        """Track Creator Economy specific processing"""
        try:
            creator_context = step.creator_context
            creator_id = creator_context.get("creator_id")
            
            if creator_id:
                # Track monetization lineage
                if step.processing_type in [ProcessingType.MODEL_TRAINING, ProcessingType.MODEL_INFERENCE]:
                    if creator_id not in self._monetization_lineage:
                        self._monetization_lineage[creator_id] = {
                            "models_trained": [],
                            "inferences_made": [],
                            "revenue_potential": 0.0,
                            "content_usage": []
                        }
                    
                    monetization_data = self._monetization_lineage[creator_id]
                    
                    if step.processing_type == ProcessingType.MODEL_TRAINING:
                        monetization_data["models_trained"].append({
                            "step_id": step.step_id,
                            "timestamp": step.executed_at.isoformat(),
                            "inputs": step.inputs,
                            "outputs": step.outputs
                        })
                    else:  # MODEL_INFERENCE
                        monetization_data["inferences_made"].append({
                            "step_id": step.step_id,
                            "timestamp": step.executed_at.isoformat(),
                            "inputs": step.inputs
                        })
                
                # Update creator data mapping
                if creator_id in self._creator_data_mapping:
                    creator_mapping = self._creator_data_mapping[creator_id]
                    creator_mapping.setdefault("processing_history", []).append({
                        "step_id": step.step_id,
                        "processing_type": step.processing_type.value,
                        "timestamp": step.executed_at.isoformat()
                    })
            
        except Exception as e:
            logger.error(f"❌ Creator processing tracking error: {str(e)}")
    
    async def _log_lineage_event(self, event_type: LineageEvent, entity_id: str, details: Dict[str, Any]) -> None:
        """Log lineage event"""
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type.value,
                "entity_id": entity_id,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            
            self._lineage_events.append(event)
            
        except Exception as e:
            logger.error(f"❌ Event logging error: {str(e)}")
    
    def get_lineage_for_asset(self, asset_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """Get complete lineage for a data asset"""
        try:
            if asset_id not in self._data_assets:
                return {"error": "Asset not found"}
            
            # Get upstream and downstream lineage using graph traversal
            upstream = self._get_upstream_lineage(asset_id, max_depth)
            downstream = self._get_downstream_lineage(asset_id, max_depth)
            
            # Get processing steps involved
            involved_steps = set()
            for node in upstream + downstream + [asset_id]:
                if node in self._lineage_by_asset:
                    # Find processing steps that connect to this asset
                    for step_id, step in self._processing_steps.items():
                        if node in step.inputs or node in step.outputs:
                            involved_steps.add(step_id)
            
            # Construct lineage record
            lineage = {
                "asset_id": asset_id,
                "asset_info": self._data_assets[asset_id].to_dict(),
                "upstream_assets": upstream,
                "downstream_assets": downstream,
                "processing_steps": [
                    self._processing_steps[step_id].to_dict() 
                    for step_id in involved_steps
                    if step_id in self._processing_steps
                ],
                "privacy_lineage": self._privacy_lineage.get(asset_id, {}),
                "quality_lineage": self._quality_lineage.get(asset_id, {}),
                "creator_context": self._get_creator_context_for_asset(asset_id),
                "lineage_depth": {
                    "upstream": len(upstream),
                    "downstream": len(downstream)
                }
            }
            
            return lineage
            
        except Exception as e:
            logger.error(f"❌ Lineage retrieval error: {str(e)}")
            return {"error": str(e)}
    
    def _get_upstream_lineage(self, asset_id: str, max_depth: int) -> List[str]:
        """Get upstream lineage assets"""
        try:
            if not self._lineage_graph.has_node(asset_id):
                return []
            
            # Use BFS to find upstream nodes
            upstream = []
            visited = set()
            queue = deque([(asset_id, 0)])
            
            while queue:
                current_asset, depth = queue.popleft()
                
                if depth >= max_depth or current_asset in visited:
                    continue
                
                visited.add(current_asset)
                
                # Get predecessors (upstream assets)
                for predecessor in self._lineage_graph.predecessors(current_asset):
                    if predecessor not in visited:
                        upstream.append(predecessor)
                        queue.append((predecessor, depth + 1))
            
            return upstream
            
        except Exception as e:
            logger.error(f"❌ Upstream lineage error: {str(e)}")
            return []
    
    def _get_downstream_lineage(self, asset_id: str, max_depth: int) -> List[str]:
        """Get downstream lineage assets"""
        try:
            if not self._lineage_graph.has_node(asset_id):
                return []
            
            # Use BFS to find downstream nodes
            downstream = []
            visited = set()
            queue = deque([(asset_id, 0)])
            
            while queue:
                current_asset, depth = queue.popleft()
                
                if depth >= max_depth or current_asset in visited:
                    continue
                
                visited.add(current_asset)
                
                # Get successors (downstream assets)
                for successor in self._lineage_graph.successors(current_asset):
                    if successor not in visited:
                        downstream.append(successor)
                        queue.append((successor, depth + 1))
            
            return downstream
            
        except Exception as e:
            logger.error(f"❌ Downstream lineage error: {str(e)}")
            return []
    
    def _get_creator_context_for_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get creator context for an asset"""
        if asset_id in self._data_assets:
            asset = self._data_assets[asset_id]
            return asset.creator_context
        return None
    
    async def analyze_impact(self, asset_id: str, change_type: str = "modification") -> ImpactAnalysis:
        """Analyze impact of changes to a data asset"""
        try:
            if asset_id not in self._data_assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            asset = self._data_assets[asset_id]
            
            # Get lineage information
            lineage = self.get_lineage_for_asset(asset_id)
            
            upstream_count = len(lineage.get("upstream_assets", []))
            downstream_count = len(lineage.get("downstream_assets", []))
            
            # Analyze affected creators
            affected_creators = set()
            affected_models = set()
            
            # Check downstream assets for creator impact
            for downstream_asset_id in lineage.get("downstream_assets", []):
                if downstream_asset_id in self._data_assets:
                    downstream_asset = self._data_assets[downstream_asset_id]
                    if downstream_asset.creator_context and "creator_id" in downstream_asset.creator_context:
                        affected_creators.add(downstream_asset.creator_context["creator_id"])
            
            # Check processing steps for model impact
            for step_data in lineage.get("processing_steps", []):
                if step_data.get("processing_type") in ["model_training", "model_inference"]:
                    # Extract model information from step parameters
                    model_name = step_data.get("parameters", {}).get("model_name")
                    if model_name:
                        affected_models.add(model_name)
            
            # Assess privacy impact
            privacy_impact = self._assess_privacy_impact(asset, change_type)
            
            # Assess business impact
            business_impact = self._assess_business_impact(asset, len(affected_creators), len(affected_models))
            
            # Generate recommendations
            recommendations = self._generate_impact_recommendations(
                asset, change_type, privacy_impact, business_impact, downstream_count
            )
            
            analysis = ImpactAnalysis(
                analysis_id=str(uuid.uuid4()),
                asset_id=asset_id,
                downstream_count=downstream_count,
                upstream_count=upstream_count,
                affected_creators=list(affected_creators),
                affected_models=list(affected_models),
                privacy_impact=privacy_impact,
                business_impact=business_impact,
                recommendations=recommendations,
                analysis_timestamp=datetime.now()
            )
            
            self._tracker_metrics["impact_analyses"] += 1
            
            logger.info(f"📊 Impact analysis completed for asset {asset_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Impact analysis error: {str(e)}")
            raise
    
    def _assess_privacy_impact(self, asset: DataAsset, change_type: str) -> str:
        """Assess privacy impact of asset changes"""
        base_privacy_level = self._assess_privacy_level(asset)
        
        if asset.classification in [DataClassification.CREATOR_PERSONAL, DataClassification.RESTRICTED]:
            if change_type in ["deletion", "schema_change"]:
                return "critical"
            elif change_type == "modification":
                return "high"
            else:
                return "medium"
        
        elif asset.classification in [DataClassification.CREATOR_CONTENT, DataClassification.MONETIZATION_DATA]:
            if change_type == "deletion":
                return "high"
            elif change_type in ["modification", "schema_change"]:
                return "medium"
            else:
                return "low"
        
        else:
            return "low"
    
    def _assess_business_impact(self, asset: DataAsset, affected_creators: int, affected_models: int) -> str:
        """Assess business impact of asset changes"""
        # High impact if many creators or models affected
        if affected_creators > 100 or affected_models > 10:
            return "critical"
        elif affected_creators > 50 or affected_models > 5:
            return "high"
        elif affected_creators > 10 or affected_models > 2:
            return "medium"
        elif affected_creators > 0 or affected_models > 0:
            return "low"
        else:
            return "none"
    
    def _generate_impact_recommendations(
        self,
        asset: DataAsset,
        change_type: str,
        privacy_impact: str,
        business_impact: str,
        downstream_count: int
    ) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []
        
        # Privacy-based recommendations
        if privacy_impact in ["critical", "high"]:
            recommendations.append("Conduct privacy impact assessment before proceeding")
            recommendations.append("Notify affected creators and obtain consent if required")
            
        # Business impact recommendations
        if business_impact in ["critical", "high"]:
            recommendations.append("Coordinate with business stakeholders before changes")
            recommendations.append("Plan phased rollout to minimize disruption")
            
        # Change-type specific recommendations
        if change_type == "deletion":
            recommendations.append("Ensure data retention policies are followed")
            recommendations.append("Create backup before deletion")
            
        elif change_type == "schema_change":
            recommendations.append("Validate downstream compatibility")
            recommendations.append("Update data contracts and documentation")
            
        # Downstream impact recommendations
        if downstream_count > 10:
            recommendations.append("Test all downstream dependencies")
            recommendations.append("Prepare rollback plan")
            
        return recommendations
    
    def get_creator_data_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get data summary for a specific creator"""
        try:
            if creator_id not in self._creator_data_mapping:
                return {"error": "Creator not found"}
            
            creator_mapping = self._creator_data_mapping[creator_id]
            
            # Get detailed asset information
            creator_assets = []
            for asset_id in creator_mapping["assets"]:
                if asset_id in self._data_assets:
                    asset = self._data_assets[asset_id]
                    creator_assets.append({
                        "asset_id": asset_id,
                        "name": asset.name,
                        "classification": asset.classification.value,
                        "size_bytes": asset.size_bytes,
                        "created_at": asset.created_at.isoformat(),
                        "privacy_level": self._privacy_lineage.get(asset_id, {}).get("privacy_level", "unknown")
                    })
            
            # Get monetization information
            monetization_info = self._monetization_lineage.get(creator_id, {})
            
            summary = {
                "creator_id": creator_id,
                "total_assets": len(creator_mapping["assets"]),
                "total_size_bytes": creator_mapping["total_size"],
                "data_classifications": list(creator_mapping["classifications"]),
                "assets": creator_assets,
                "monetization": {
                    "models_trained": len(monetization_info.get("models_trained", [])),
                    "inferences_made": len(monetization_info.get("inferences_made", [])),
                    "revenue_potential": monetization_info.get("revenue_potential", 0.0)
                },
                "privacy_summary": {
                    "gdpr_applicable_assets": len([
                        a for a in creator_assets 
                        if self._privacy_lineage.get(a["asset_id"], {}).get("gdpr_applicable", False)
                    ]),
                    "high_privacy_assets": len([
                        a for a in creator_assets 
                        if a["privacy_level"] in ["high", "critical"]
                    ])
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Creator data summary error: {str(e)}")
            return {"error": str(e)}
    
    def search_lineage(
        self,
        query: str,
        search_type: str = "asset_name",
        creator_id: Optional[str] = None,
        classification: Optional[DataClassification] = None
    ) -> List[Dict[str, Any]]:
        """Search lineage records"""
        try:
            results = []
            
            # Filter assets based on criteria
            candidate_assets = []
            
            if creator_id:
                candidate_assets = list(self._assets_by_creator.get(creator_id, set()))
            elif classification:
                candidate_assets = list(self._assets_by_classification.get(classification, set()))
            else:
                candidate_assets = list(self._data_assets.keys())
            
            # Apply search filter
            for asset_id in candidate_assets:
                if asset_id not in self._data_assets:
                    continue
                    
                asset = self._data_assets[asset_id]
                match = False
                
                if search_type == "asset_name" and query.lower() in asset.name.lower():
                    match = True
                elif search_type == "location" and query.lower() in asset.location.lower():
                    match = True
                elif search_type == "owner" and query.lower() in asset.owner.lower():
                    match = True
                
                if match:
                    lineage = self.get_lineage_for_asset(asset_id, max_depth=3)
                    results.append(lineage)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Lineage search error: {str(e)}")
            return []
    
    def get_tracking_metrics(self) -> Dict[str, Any]:
        """Get lineage tracker metrics"""
        return {
            **self._tracker_metrics,
            "total_nodes": self._lineage_graph.number_of_nodes(),
            "total_edges": self._lineage_graph.number_of_edges(),
            "creators_tracked": len(self._creator_data_mapping),
            "privacy_records": len(self._privacy_lineage),
            "quality_records": len(self._quality_lineage),
            "recent_events": len(self._lineage_events)
        }
    
    def health_check(self) -> str:
        """Health check for lineage tracker"""
        try:
            # Check graph consistency
            if self._lineage_graph.number_of_nodes() != len(self._data_assets):
                return "WARNING: Graph node count mismatch with asset count"
            
            # Check for orphaned assets
            orphaned_assets = [
                asset_id for asset_id in self._data_assets.keys()
                if not self._lineage_graph.has_node(asset_id)
            ]
            
            if orphaned_assets:
                return f"WARNING: {len(orphaned_assets)} orphaned assets detected"
            
            # Check for cycles (should not exist in most cases)
            if not nx.is_directed_acyclic_graph(self._lineage_graph):
                return "WARNING: Cycles detected in lineage graph"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and enums
__all__ = [
    "DataLineageTracker",
    "DataSourceType",
    "ProcessingType", 
    "DataClassification",
    "LineageEvent",
    "DataAsset",
    "ProcessingStep",
    "LineageRecord",
    "ImpactAnalysis"
]