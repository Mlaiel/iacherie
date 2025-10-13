"""📦 Model Versioning Controller - Enterprise ML Deployment Versioning
============================================================
Module: mlops/model_deployment/model_versioning_controller.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE MODEL VERSIONING CONTROLLER
Advanced model versioning system specialized for deployment scenarios
- Deployment-specific version tracking
- Rollback capability management
- Creator-specific version isolation
- Performance comparison across deployed versions
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import semver
import pickle

logger = logging.getLogger(__name__)

class DeploymentVersionType(Enum):
    """Version increment types for deployments"""
    MAJOR = "major"  # Breaking changes or major model updates
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, performance improvements
    HOTFIX = "hotfix"  # Critical fixes for production

class ModelDeploymentStatus(Enum):
    """Model deployment version status"""
    BUILDING = "building"
    TESTING = "testing"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"
    ROLLED_BACK = "rolled_back"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class RollbackStrategy(Enum):
    """Rollback strategies for model versions"""
    IMMEDIATE = "immediate"  # Instant switch
    GRADUAL = "gradual"     # Gradual traffic shift
    BLUE_GREEN = "blue_green"  # Blue-green deployment
    CANARY_REVERSE = "canary_reverse"  # Reverse canary

@dataclass
class DeploymentVersion:
    """Model deployment version metadata"""
    model_id: str
    version: str
    creator_id: str
    deployment_id: str
    status: ModelDeploymentStatus
    created_at: datetime
    deployed_at: Optional[datetime] = None
    artifacts_path: str = ""
    container_tag: str = ""
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    traffic_percentage: float = 0.0
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    signature: str = ""
    creator_tier: str = "creator"

@dataclass
class VersionComparison:
    """Version comparison result for deployments"""
    baseline_version: str
    target_version: str
    performance_diff: Dict[str, float]
    compatibility_score: float
    recommendation: str
    rollback_risk: str
    traffic_recommendation: float

class ModelVersioningController:
    """📦 Enterprise Model Versioning Controller for Deployments
    
    Specialized version control system for ML model deployments in Creator Economy.
    Manages deployment-specific versioning, rollback capabilities, and performance tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the model versioning controller"""
        self.config = config or {}
        self.registry_path = Path(self.config.get('registry_path', './deployment_registry'))
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        # Version storage
        self.deployment_versions: Dict[str, List[DeploymentVersion]] = {}
        self.active_versions: Dict[str, str] = {}  # model_id -> active_version
        self.creator_versions: Dict[str, Dict[str, List[str]]] = {}  # creator_id -> model_id -> versions
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.rollback_history: List[Dict[str, Any]] = []
        
        # Version policies per creator tier
        self.tier_policies = self._setup_tier_policies()
        
        logger.info("ModelVersioningController initialized for deployment management")
    
    def _setup_tier_policies(self) -> Dict[str, Dict[str, Any]]:
        """Setup version policies per creator tier"""
        return {
            'free': {
                'max_versions': 3,
                'retention_days': 30,
                'rollback_allowed': True,
                'canary_testing': False,
                'blue_green': False
            },
            'creator': {
                'max_versions': 10,
                'retention_days': 90,
                'rollback_allowed': True,
                'canary_testing': True,
                'blue_green': False
            },
            'professional': {
                'max_versions': 25,
                'retention_days': 180,
                'rollback_allowed': True,
                'canary_testing': True,
                'blue_green': True
            },
            'enterprise': {
                'max_versions': 100,
                'retention_days': 365,
                'rollback_allowed': True,
                'canary_testing': True,
                'blue_green': True
            }
        }
    
    async def create_deployment_version(
        self,
        model_id: str,
        creator_id: str,
        deployment_id: str,
        artifacts_path: str,
        version_type: DeploymentVersionType = DeploymentVersionType.MINOR,
        container_tag: str = "",
        deployment_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> DeploymentVersion:
        """🆕 Create new deployment version
        
        Args:
            model_id: Unique model identifier
            creator_id: Creator who owns the model
            deployment_id: Associated deployment ID
            artifacts_path: Path to model artifacts
            version_type: Type of version increment
            container_tag: Container image tag
            deployment_config: Deployment configuration
            metadata: Additional version metadata
            tags: Version tags
            
        Returns:
            Created deployment version
        """
        try:
            # Get creator tier and policies
            creator_tier = metadata.get('creator_tier', 'creator') if metadata else 'creator'
            tier_policy = self.tier_policies.get(creator_tier, self.tier_policies['creator'])
            
            # Generate version number
            version_number = await self._generate_version_number(model_id, version_type)
            
            # Calculate artifact signature
            signature = await self._calculate_artifact_signature(artifacts_path)
            
            # Create deployment version
            deployment_version = DeploymentVersion(
                model_id=model_id,
                version=version_number,
                creator_id=creator_id,
                deployment_id=deployment_id,
                status=ModelDeploymentStatus.BUILDING,
                created_at=datetime.now(),
                artifacts_path=artifacts_path,
                container_tag=container_tag or f"{model_id}:{version_number}",
                deployment_config=deployment_config or {},
                metadata=metadata or {},
                tags=tags or [],
                signature=signature,
                creator_tier=creator_tier
            )
            
            # Store version
            if model_id not in self.deployment_versions:
                self.deployment_versions[model_id] = []
            
            self.deployment_versions[model_id].append(deployment_version)
            
            # Update creator version tracking
            if creator_id not in self.creator_versions:
                self.creator_versions[creator_id] = {}
            if model_id not in self.creator_versions[creator_id]:
                self.creator_versions[creator_id][model_id] = []
            
            self.creator_versions[creator_id][model_id].append(version_number)
            
            # Enforce version limits
            await self._enforce_version_limits(model_id, creator_id, tier_policy)
            
            # Persist version
            await self._persist_version(deployment_version)
            
            logger.info(f"Created deployment version {version_number} for model {model_id}")
            return deployment_version
            
        except Exception as e:
            logger.error(f"Failed to create deployment version: {str(e)}")
            raise
    
    async def _generate_version_number(
        self,
        model_id: str,
        version_type: DeploymentVersionType
    ) -> str:
        """Generate semantic version number"""
        try:
            # Get latest version
            latest_version = await self.get_latest_deployment_version(model_id)
            
            if not latest_version:
                return "1.0.0"
            
            # Parse existing version
            current_version = semver.VersionInfo.parse(latest_version.version)
            
            # Increment based on type
            if version_type == DeploymentVersionType.MAJOR:
                new_version = current_version.bump_major()
            elif version_type == DeploymentVersionType.MINOR:
                new_version = current_version.bump_minor()
            elif version_type == DeploymentVersionType.PATCH:
                new_version = current_version.bump_patch()
            elif version_type == DeploymentVersionType.HOTFIX:
                # Hotfix increments patch with hotfix suffix
                new_version = current_version.bump_patch()
                new_version = semver.VersionInfo(
                    new_version.major,
                    new_version.minor,
                    new_version.patch,
                    prerelease=f"hotfix.{int(datetime.now().timestamp())}"
                )
            
            return str(new_version)
            
        except Exception as e:
            logger.error(f"Failed to generate version number: {str(e)}")
            return "1.0.0"
    
    async def _calculate_artifact_signature(self, artifacts_path: str) -> str:
        """Calculate signature for model artifacts"""
        try:
            # In real implementation, this would hash all model files
            # For now, create a placeholder signature
            content = f"{artifacts_path}_{datetime.now().isoformat()}"
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        except Exception as e:
            logger.error(f"Failed to calculate signature: {str(e)}")
            return "unknown_signature"
    
    async def promote_version(
        self,
        model_id: str,
        version: str,
        target_status: ModelDeploymentStatus,
        traffic_percentage: float = 0.0
    ) -> bool:
        """🚀 Promote deployment version to target status
        
        Args:
            model_id: Model identifier
            version: Version to promote
            target_status: Target deployment status
            traffic_percentage: Traffic percentage for gradual rollout
            
        Returns:
            True if promotion successful, False otherwise
        """
        try:
            deployment_version = await self.get_deployment_version(model_id, version)
            if not deployment_version:
                logger.error(f"Version {version} not found for model {model_id}")
                return False
            
            # Validate promotion
            if not self._validate_promotion(deployment_version, target_status):
                logger.error(f"Invalid promotion from {deployment_version.status} to {target_status}")
                return False
            
            # Update version status
            old_status = deployment_version.status
            deployment_version.status = target_status
            deployment_version.traffic_percentage = traffic_percentage
            
            if target_status == ModelDeploymentStatus.PRODUCTION:
                deployment_version.deployed_at = datetime.now()
                self.active_versions[model_id] = version
            
            # Record promotion event
            await self._record_version_event(
                model_id,
                version,
                'promotion',
                {
                    'from_status': old_status.value,
                    'to_status': target_status.value,
                    'traffic_percentage': traffic_percentage
                }
            )
            
            # Persist changes
            await self._persist_version(deployment_version)
            
            logger.info(f"Promoted version {version} to {target_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote version {version}: {str(e)}")
            return False
    
    def _validate_promotion(
        self,
        version: DeploymentVersion,
        target_status: ModelDeploymentStatus
    ) -> bool:
        """Validate version promotion"""
        current_status = version.status
        
        # Define valid promotion paths
        valid_transitions = {
            ModelDeploymentStatus.BUILDING: [
                ModelDeploymentStatus.TESTING,
                ModelDeploymentStatus.DEPRECATED
            ],
            ModelDeploymentStatus.TESTING: [
                ModelDeploymentStatus.STAGING,
                ModelDeploymentStatus.BUILDING,
                ModelDeploymentStatus.DEPRECATED
            ],
            ModelDeploymentStatus.STAGING: [
                ModelDeploymentStatus.CANARY,
                ModelDeploymentStatus.PRODUCTION,
                ModelDeploymentStatus.TESTING,
                ModelDeploymentStatus.DEPRECATED
            ],
            ModelDeploymentStatus.CANARY: [
                ModelDeploymentStatus.PRODUCTION,
                ModelDeploymentStatus.ROLLED_BACK,
                ModelDeploymentStatus.STAGING
            ],
            ModelDeploymentStatus.PRODUCTION: [
                ModelDeploymentStatus.ROLLED_BACK,
                ModelDeploymentStatus.DEPRECATED
            ],
            ModelDeploymentStatus.ROLLED_BACK: [
                ModelDeploymentStatus.STAGING,
                ModelDeploymentStatus.DEPRECATED
            ],
            ModelDeploymentStatus.DEPRECATED: [
                ModelDeploymentStatus.RETIRED
            ]
        }
        
        return target_status in valid_transitions.get(current_status, [])
    
    async def rollback_deployment(
        self,
        model_id: str,
        target_version: Optional[str] = None,
        strategy: RollbackStrategy = RollbackStrategy.IMMEDIATE
    ) -> Dict[str, Any]:
        """🔄 Rollback deployment to previous version
        
        Args:
            model_id: Model identifier
            target_version: Specific version to rollback to (optional)
            strategy: Rollback strategy
            
        Returns:
            Rollback result with details
        """
        try:
            # Get current active version
            current_version = self.active_versions.get(model_id)
            if not current_version:
                return {
                    'success': False,
                    'error': f'No active version found for model {model_id}'
                }
            
            # Determine target version
            if not target_version:
                target_version = await self._get_previous_stable_version(model_id, current_version)
                if not target_version:
                    return {
                        'success': False,
                        'error': 'No previous stable version available for rollback'
                    }
            
            # Get target version details
            target_deployment_version = await self.get_deployment_version(model_id, target_version)
            if not target_deployment_version:
                return {
                    'success': False,
                    'error': f'Target version {target_version} not found'
                }
            
            # Validate rollback capability
            creator_tier = target_deployment_version.creator_tier
            tier_policy = self.tier_policies.get(creator_tier, self.tier_policies['creator'])
            
            if not tier_policy.get('rollback_allowed', True):
                return {
                    'success': False,
                    'error': f'Rollback not allowed for tier {creator_tier}'
                }
            
            # Execute rollback based on strategy
            rollback_result = await self._execute_rollback(
                model_id,
                current_version,
                target_version,
                strategy
            )
            
            if rollback_result['success']:
                # Update version statuses
                current_deployment_version = await self.get_deployment_version(model_id, current_version)
                if current_deployment_version:
                    current_deployment_version.status = ModelDeploymentStatus.ROLLED_BACK
                    current_deployment_version.traffic_percentage = 0.0
                
                target_deployment_version.status = ModelDeploymentStatus.PRODUCTION
                target_deployment_version.traffic_percentage = 100.0
                
                # Update active version
                self.active_versions[model_id] = target_version
                
                # Record rollback event
                rollback_event = {
                    'model_id': model_id,
                    'from_version': current_version,
                    'to_version': target_version,
                    'strategy': strategy.value,
                    'timestamp': datetime.now().isoformat(),
                    'result': rollback_result
                }
                self.rollback_history.append(rollback_event)
                
                # Persist changes
                await self._persist_version(current_deployment_version)
                await self._persist_version(target_deployment_version)
                
                logger.info(f"Rollback completed: {current_version} -> {target_version}")
            
            return rollback_result
            
        except Exception as e:
            logger.error(f"Rollback failed for model {model_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _get_previous_stable_version(self, model_id: str, current_version: str) -> Optional[str]:
        """Get previous stable version for rollback"""
        try:
            versions = self.deployment_versions.get(model_id, [])
            if not versions:
                return None
            
            # Sort versions by creation time
            sorted_versions = sorted(
                versions,
                key=lambda v: v.created_at,
                reverse=True
            )
            
            # Find current version index
            current_index = -1
            for i, version in enumerate(sorted_versions):
                if version.version == current_version:
                    current_index = i
                    break
            
            if current_index == -1:
                return None
            
            # Find previous stable version
            for i in range(current_index + 1, len(sorted_versions)):
                version = sorted_versions[i]
                if version.status in [
                    ModelDeploymentStatus.PRODUCTION,
                    ModelDeploymentStatus.STAGING
                ] and version.status != ModelDeploymentStatus.ROLLED_BACK:
                    return version.version
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get previous stable version: {str(e)}")
            return None
    
    async def _execute_rollback(
        self,
        model_id: str,
        current_version: str,
        target_version: str,
        strategy: RollbackStrategy
    ) -> Dict[str, Any]:
        """Execute rollback using specified strategy"""
        try:
            # Get rollback data from current version
            current_deployment_version = await self.get_deployment_version(model_id, current_version)
            rollback_data = current_deployment_version.rollback_data if current_deployment_version else {}
            
            if strategy == RollbackStrategy.IMMEDIATE:
                return await self._execute_immediate_rollback(
                    model_id, current_version, target_version, rollback_data
                )
            elif strategy == RollbackStrategy.GRADUAL:
                return await self._execute_gradual_rollback(
                    model_id, current_version, target_version, rollback_data
                )
            elif strategy == RollbackStrategy.BLUE_GREEN:
                return await self._execute_blue_green_rollback(
                    model_id, current_version, target_version, rollback_data
                )
            elif strategy == RollbackStrategy.CANARY_REVERSE:
                return await self._execute_canary_reverse_rollback(
                    model_id, current_version, target_version, rollback_data
                )
            else:
                return {'success': False, 'error': f'Unknown rollback strategy: {strategy}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_immediate_rollback(
        self,
        model_id: str,
        current_version: str,
        target_version: str,
        rollback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute immediate rollback"""
        try:
            # Simulate immediate rollback
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'message': f'Immediate rollback completed: {current_version} -> {target_version}',
                'rollback_time': datetime.now().isoformat(),
                'strategy': 'immediate'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_gradual_rollback(
        self,
        model_id: str,
        current_version: str,
        target_version: str,
        rollback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute gradual rollback with traffic shifting"""
        try:
            # Simulate gradual rollback
            await asyncio.sleep(2)
            
            return {
                'success': True,
                'message': f'Gradual rollback completed: {current_version} -> {target_version}',
                'rollback_time': datetime.now().isoformat(),
                'strategy': 'gradual',
                'traffic_shift_duration': '5 minutes'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_blue_green_rollback(
        self,
        model_id: str,
        current_version: str,
        target_version: str,
        rollback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute blue-green rollback"""
        try:
            # Simulate blue-green rollback
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'message': f'Blue-green rollback completed: {current_version} -> {target_version}',
                'rollback_time': datetime.now().isoformat(),
                'strategy': 'blue_green'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_canary_reverse_rollback(
        self,
        model_id: str,
        current_version: str,
        target_version: str,
        rollback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute canary reverse rollback"""
        try:
            # Simulate canary reverse rollback
            await asyncio.sleep(3)
            
            return {
                'success': True,
                'message': f'Canary reverse rollback completed: {current_version} -> {target_version}',
                'rollback_time': datetime.now().isoformat(),
                'strategy': 'canary_reverse',
                'canary_percentage': '10% -> 0%'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def compare_deployment_versions(
        self,
        model_id: str,
        baseline_version: str,
        target_version: str
    ) -> VersionComparison:
        """📊 Compare deployment versions for decision making"""
        try:
            baseline = await self.get_deployment_version(model_id, baseline_version)
            target = await self.get_deployment_version(model_id, target_version)
            
            if not baseline or not target:
                raise ValueError("One or both versions not found")
            
            # Compare performance metrics
            performance_diff = {}
            for metric in baseline.performance_metrics:
                baseline_value = baseline.performance_metrics[metric]
                target_value = target.performance_metrics.get(metric, 0)
                
                if baseline_value != 0:
                    diff = ((target_value - baseline_value) / baseline_value) * 100
                    performance_diff[metric] = round(diff, 2)
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(baseline, target)
            
            # Generate recommendation
            recommendation = self._generate_version_recommendation(
                baseline, target, performance_diff, compatibility_score
            )
            
            # Assess rollback risk
            rollback_risk = self._assess_rollback_risk(target)
            
            # Traffic recommendation
            traffic_recommendation = self._calculate_traffic_recommendation(
                performance_diff, compatibility_score
            )
            
            return VersionComparison(
                baseline_version=baseline_version,
                target_version=target_version,
                performance_diff=performance_diff,
                compatibility_score=compatibility_score,
                recommendation=recommendation,
                rollback_risk=rollback_risk,
                traffic_recommendation=traffic_recommendation
            )
            
        except Exception as e:
            logger.error(f"Version comparison failed: {str(e)}")
            raise
    
    def _calculate_compatibility_score(
        self,
        baseline: DeploymentVersion,
        target: DeploymentVersion
    ) -> float:
        """Calculate compatibility score between versions"""
        try:
            score = 100.0
            
            # Check semantic version compatibility
            baseline_semver = semver.VersionInfo.parse(baseline.version)
            target_semver = semver.VersionInfo.parse(target.version)
            
            if target_semver.major != baseline_semver.major:
                score -= 30  # Major version change
            elif target_semver.minor != baseline_semver.minor:
                score -= 10  # Minor version change
            
            # Check deployment config compatibility
            baseline_config = baseline.deployment_config
            target_config = target.deployment_config
            
            config_diff_count = 0
            for key in baseline_config:
                if key not in target_config:
                    config_diff_count += 1
                elif baseline_config[key] != target_config[key]:
                    config_diff_count += 1
            
            score -= min(config_diff_count * 5, 20)  # Max 20 points for config differences
            
            return max(score, 0.0)
            
        except Exception as e:
            logger.error(f"Compatibility score calculation failed: {str(e)}")
            return 50.0  # Default score
    
    def _generate_version_recommendation(
        self,
        baseline: DeploymentVersion,
        target: DeploymentVersion,
        performance_diff: Dict[str, float],
        compatibility_score: float
    ) -> str:
        """Generate version recommendation"""
        try:
            if compatibility_score < 50:
                return "HIGH_RISK: Low compatibility score. Consider thorough testing."
            
            # Check performance improvements
            avg_improvement = sum(performance_diff.values()) / len(performance_diff) if performance_diff else 0
            
            if avg_improvement > 10:
                return "RECOMMENDED: Significant performance improvements detected."
            elif avg_improvement > 0:
                return "SUITABLE: Minor performance improvements. Safe to deploy."
            elif avg_improvement > -5:
                return "NEUTRAL: No significant performance changes."
            else:
                return "CAUTION: Performance degradation detected. Review carefully."
                
        except Exception as e:
            return "UNKNOWN: Unable to generate recommendation."
    
    def _assess_rollback_risk(self, version: DeploymentVersion) -> str:
        """Assess rollback risk for version"""
        try:
            risk_factors = []
            
            # Check if version has rollback data
            if not version.rollback_data:
                risk_factors.append("No rollback data available")
            
            # Check version age
            age_days = (datetime.now() - version.created_at).days
            if age_days > 30:
                risk_factors.append("Version is older than 30 days")
            
            # Check if version was previously rolled back
            if version.status == ModelDeploymentStatus.ROLLED_BACK:
                risk_factors.append("Version was previously rolled back")
            
            if len(risk_factors) == 0:
                return "LOW"
            elif len(risk_factors) <= 2:
                return "MEDIUM"
            else:
                return "HIGH"
                
        except Exception as e:
            return "UNKNOWN"
    
    def _calculate_traffic_recommendation(
        self,
        performance_diff: Dict[str, float],
        compatibility_score: float
    ) -> float:
        """Calculate recommended traffic percentage"""
        try:
            if compatibility_score < 50:
                return 5.0  # Very low traffic for high risk
            
            avg_improvement = sum(performance_diff.values()) / len(performance_diff) if performance_diff else 0
            
            if avg_improvement > 20:
                return 100.0  # Full traffic for major improvements
            elif avg_improvement > 10:
                return 50.0  # Half traffic for good improvements
            elif avg_improvement > 0:
                return 25.0  # Quarter traffic for minor improvements
            else:
                return 10.0  # Small traffic for neutral/negative changes
                
        except Exception as e:
            return 10.0  # Default conservative recommendation
    
    async def get_deployment_version(self, model_id: str, version: str) -> Optional[DeploymentVersion]:
        """Get specific deployment version"""
        versions = self.deployment_versions.get(model_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None
    
    async def get_latest_deployment_version(self, model_id: str) -> Optional[DeploymentVersion]:
        """Get latest deployment version"""
        versions = self.deployment_versions.get(model_id, [])
        if not versions:
            return None
        
        # Sort by semantic version
        try:
            sorted_versions = sorted(
                versions,
                key=lambda v: semver.VersionInfo.parse(v.version),
                reverse=True
            )
            return sorted_versions[0]
        except Exception:
            # Fallback to creation time sorting
            sorted_versions = sorted(
                versions,
                key=lambda v: v.created_at,
                reverse=True
            )
            return sorted_versions[0]
    
    async def get_creator_versions(self, creator_id: str, model_id: Optional[str] = None) -> Dict[str, List[str]]:
        """Get versions for creator"""
        creator_versions = self.creator_versions.get(creator_id, {})
        
        if model_id:
            return {model_id: creator_versions.get(model_id, [])}
        
        return creator_versions
    
    async def _enforce_version_limits(
        self,
        model_id: str,
        creator_id: str,
        tier_policy: Dict[str, Any]
    ) -> None:
        """Enforce version limits based on creator tier"""
        try:
            max_versions = tier_policy.get('max_versions', 10)
            versions = self.deployment_versions.get(model_id, [])
            
            if len(versions) > max_versions:
                # Sort by creation time and remove oldest
                sorted_versions = sorted(versions, key=lambda v: v.created_at)
                versions_to_remove = sorted_versions[:-max_versions]
                
                for version in versions_to_remove:
                    # Only remove if not active or in critical status
                    if (version.status not in [
                        ModelDeploymentStatus.PRODUCTION,
                        ModelDeploymentStatus.CANARY
                    ] and version.version != self.active_versions.get(model_id)):
                        versions.remove(version)
                        logger.info(f"Removed old version {version.version} for model {model_id}")
                
        except Exception as e:
            logger.error(f"Failed to enforce version limits: {str(e)}")
    
    async def _record_version_event(
        self,
        model_id: str,
        version: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Record version event for audit trail"""
        try:
            event = {
                'model_id': model_id,
                'version': version,
                'event_type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # In real implementation, this would be persisted to database
            logger.info(f"Version event recorded: {event_type} for {model_id}:{version}")
            
        except Exception as e:
            logger.error(f"Failed to record version event: {str(e)}")
    
    async def _persist_version(self, version: DeploymentVersion) -> None:
        """Persist version metadata to storage"""
        try:
            version_file = self.registry_path / f"{version.model_id}_{version.version}.json"
            
            version_data = {
                'model_id': version.model_id,
                'version': version.version,
                'creator_id': version.creator_id,
                'deployment_id': version.deployment_id,
                'status': version.status.value,
                'created_at': version.created_at.isoformat(),
                'deployed_at': version.deployed_at.isoformat() if version.deployed_at else None,
                'artifacts_path': version.artifacts_path,
                'container_tag': version.container_tag,
                'performance_metrics': version.performance_metrics,
                'deployment_config': version.deployment_config,
                'traffic_percentage': version.traffic_percentage,
                'rollback_data': version.rollback_data,
                'metadata': version.metadata,
                'tags': version.tags,
                'signature': version.signature,
                'creator_tier': version.creator_tier
            }
            
            with open(version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to persist version: {str(e)}")
    
    def get_deployment_metrics(self) -> Dict[str, Any]:
        """📈 Get deployment versioning metrics"""
        total_versions = sum(len(versions) for versions in self.deployment_versions.values())
        active_deployments = len(self.active_versions)
        
        # Count versions by status
        status_counts = {}
        for versions in self.deployment_versions.values():
            for version in versions:
                status = version.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_versions': total_versions,
            'active_deployments': active_deployments,
            'total_rollbacks': len(self.rollback_history),
            'status_distribution': status_counts,
            'models_tracked': len(self.deployment_versions),
            'creators_tracked': len(self.creator_versions)
        }

# Export all components
__all__ = [
    'ModelVersioningController',
    'DeploymentVersion',
    'VersionComparison',
    'DeploymentVersionType',
    'ModelDeploymentStatus',
    'RollbackStrategy'
]