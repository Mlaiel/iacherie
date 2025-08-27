"""
Versioning Module - Model versioning, experiment tracking, and A/B testing
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive model versioning capabilities including
version management, experiment tracking, and A/B testing infrastructure.
"""

import logging
import json
import hashlib
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import shutil
import uuid

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Model version status"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ExperimentStatus(Enum):
    """Experiment status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ABTestStatus(Enum):
    """A/B Test status"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class ModelVersion:
    """Model version information"""
    version_id: str
    model_name: str
    version_number: str
    status: ModelStatus
    created_at: datetime
    created_by: str
    model_path: str
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]
    tags: List[str]
    description: str = ""

@dataclass
class Experiment:
    """Experiment information"""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    artifacts: Dict[str, str]
    tags: List[str]

@dataclass
class ABTest:
    """A/B Test configuration and results"""
    test_id: str
    name: str
    description: str
    status: ABTestStatus
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    control_version: str
    treatment_versions: List[str]
    traffic_split: Dict[str, float]
    success_metrics: List[str]
    results: Dict[str, Any]
    statistical_significance: Optional[float]

class ModelVersionManager:
    """Manage model versions and lifecycle"""
    
    def __init__(self, storage_path: str = "./models"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.versions: Dict[str, ModelVersion] = {}
        self.metadata_file = self.storage_path / "versions_metadata.json"
        self._load_metadata()
        self.logger.info("ModelVersionManager initialized successfully")
    
    def _load_metadata(self):
        """Load existing version metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for version_id, version_data in data.items():
                        # Convert datetime strings back to datetime objects
                        version_data['created_at'] = datetime.fromisoformat(version_data['created_at'])
                        version_data['status'] = ModelStatus(version_data['status'])
                        self.versions[version_id] = ModelVersion(**version_data)
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
    
    def _save_metadata(self):
        """Save version metadata to disk"""
        try:
            data = {}
            for version_id, version in self.versions.items():
                version_data = asdict(version)
                version_data['created_at'] = version.created_at.isoformat()
                version_data['status'] = version.status.value
                data[version_id] = version_data
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
    
    def create_version(self, model_name: str, model_path: str, version_number: Optional[str] = None,
                      created_by: str = "system", description: str = "", 
                      metadata: Dict[str, Any] = None, tags: List[str] = None) -> str:
        """Create a new model version"""
        try:
            if version_number is None:
                version_number = self._generate_version_number(model_name)
            
            version_id = self._generate_version_id(model_name, version_number)
            
            # Copy model files to version storage
            version_dir = self.storage_path / model_name / version_number
            version_dir.mkdir(parents=True, exist_ok=True)
            
            if os.path.exists(model_path):
                if os.path.isfile(model_path):
                    shutil.copy2(model_path, version_dir / os.path.basename(model_path))
                else:
                    shutil.copytree(model_path, version_dir / "model", dirs_exist_ok=True)
            
            # Create version record
            model_version = ModelVersion(
                version_id=version_id,
                model_name=model_name,
                version_number=version_number,
                status=ModelStatus.DEVELOPMENT,
                created_at=datetime.utcnow(),
                created_by=created_by,
                model_path=str(version_dir),
                metadata=metadata or {},
                performance_metrics={},
                tags=tags or [],
                description=description
            )
            
            self.versions[version_id] = model_version
            self._save_metadata()
            
            self.logger.info(f"Created model version: {version_id}")
            return version_id
            
        except Exception as e:
            self.logger.error(f"Failed to create version: {e}")
            raise
    
    def _generate_version_number(self, model_name: str) -> str:
        """Generate next version number for a model"""
        existing_versions = [
            v for v in self.versions.values() 
            if v.model_name == model_name
        ]
        
        if not existing_versions:
            return "1.0.0"
        
        # Simple semantic versioning increment
        max_version = max(existing_versions, key=lambda x: x.created_at)
        parts = max_version.version_number.split('.')
        if len(parts) >= 2:
            minor = int(parts[1]) + 1
            return f"{parts[0]}.{minor}.0"
        
        return "1.0.0"
    
    def _generate_version_id(self, model_name: str, version_number: str) -> str:
        """Generate unique version ID"""
        unique_string = f"{model_name}:{version_number}:{int(datetime.utcnow().timestamp())}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get version by ID"""
        return self.versions.get(version_id)
    
    def list_versions(self, model_name: Optional[str] = None, 
                     status: Optional[ModelStatus] = None) -> List[ModelVersion]:
        """List model versions with optional filtering"""
        versions = list(self.versions.values())
        
        if model_name:
            versions = [v for v in versions if v.model_name == model_name]
        
        if status:
            versions = [v for v in versions if v.status == status]
        
        return sorted(versions, key=lambda x: x.created_at, reverse=True)
    
    def promote_version(self, version_id: str, target_status: ModelStatus) -> bool:
        """Promote version to target status"""
        try:
            if version_id not in self.versions:
                raise ValueError(f"Version not found: {version_id}")
            
            version = self.versions[version_id]
            old_status = version.status
            version.status = target_status
            
            self._save_metadata()
            
            self.logger.info(f"Promoted version {version_id} from {old_status.value} to {target_status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote version: {e}")
            return False
    
    def update_metrics(self, version_id: str, metrics: Dict[str, float]) -> bool:
        """Update performance metrics for a version"""
        try:
            if version_id not in self.versions:
                raise ValueError(f"Version not found: {version_id}")
            
            version = self.versions[version_id]
            version.performance_metrics.update(metrics)
            
            self._save_metadata()
            
            self.logger.info(f"Updated metrics for version {version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics: {e}")
            return False
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a model version"""
        try:
            if version_id not in self.versions:
                raise ValueError(f"Version not found: {version_id}")
            
            version = self.versions[version_id]
            
            # Only allow deletion of development versions
            if version.status == ModelStatus.PRODUCTION:
                raise ValueError("Cannot delete production version")
            
            # Remove files
            version_path = Path(version.model_path)
            if version_path.exists():
                shutil.rmtree(version_path)
            
            # Remove from tracking
            del self.versions[version_id]
            self._save_metadata()
            
            self.logger.info(f"Deleted version: {version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete version: {e}")
            return False

class ExperimentTracker:
    """Track ML experiments and their results"""
    
    def __init__(self, storage_path: str = "./experiments"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.experiments: Dict[str, Experiment] = {}
        self.metadata_file = self.storage_path / "experiments_metadata.json"
        self._load_metadata()
        self.logger.info("ExperimentTracker initialized successfully")
    
    def _load_metadata(self):
        """Load existing experiment metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for exp_id, exp_data in data.items():
                        # Convert datetime strings back to datetime objects
                        exp_data['created_at'] = datetime.fromisoformat(exp_data['created_at'])
                        if exp_data.get('started_at'):
                            exp_data['started_at'] = datetime.fromisoformat(exp_data['started_at'])
                        if exp_data.get('completed_at'):
                            exp_data['completed_at'] = datetime.fromisoformat(exp_data['completed_at'])
                        exp_data['status'] = ExperimentStatus(exp_data['status'])
                        self.experiments[exp_id] = Experiment(**exp_data)
        except Exception as e:
            self.logger.error(f"Failed to load experiment metadata: {e}")
    
    def _save_metadata(self):
        """Save experiment metadata to disk"""
        try:
            data = {}
            for exp_id, experiment in self.experiments.items():
                exp_data = asdict(experiment)
                exp_data['created_at'] = experiment.created_at.isoformat()
                if experiment.started_at:
                    exp_data['started_at'] = experiment.started_at.isoformat()
                if experiment.completed_at:
                    exp_data['completed_at'] = experiment.completed_at.isoformat()
                exp_data['status'] = experiment.status.value
                data[exp_id] = exp_data
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save experiment metadata: {e}")
    
    def create_experiment(self, name: str, description: str = "", 
                         parameters: Dict[str, Any] = None, 
                         tags: List[str] = None) -> str:
        """Create a new experiment"""
        try:
            experiment_id = str(uuid.uuid4())[:12]
            
            experiment = Experiment(
                experiment_id=experiment_id,
                name=name,
                description=description,
                status=ExperimentStatus.CREATED,
                created_at=datetime.utcnow(),
                started_at=None,
                completed_at=None,
                parameters=parameters or {},
                metrics={},
                artifacts={},
                tags=tags or []
            )
            
            self.experiments[experiment_id] = experiment
            self._save_metadata()
            
            self.logger.info(f"Created experiment: {experiment_id} - {name}")
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Failed to create experiment: {e}")
            raise
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            experiment = self.experiments[experiment_id]
            experiment.status = ExperimentStatus.RUNNING
            experiment.started_at = datetime.utcnow()
            
            self._save_metadata()
            
            self.logger.info(f"Started experiment: {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start experiment: {e}")
            return False
    
    def log_metric(self, experiment_id: str, metric_name: str, value: float) -> bool:
        """Log a metric for an experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            experiment = self.experiments[experiment_id]
            experiment.metrics[metric_name] = value
            
            self._save_metadata()
            
            self.logger.debug(f"Logged metric {metric_name}={value} for experiment {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log metric: {e}")
            return False
    
    def log_artifact(self, experiment_id: str, artifact_name: str, artifact_path: str) -> bool:
        """Log an artifact for an experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            experiment = self.experiments[experiment_id]
            experiment.artifacts[artifact_name] = artifact_path
            
            self._save_metadata()
            
            self.logger.info(f"Logged artifact {artifact_name} for experiment {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log artifact: {e}")
            return False
    
    def complete_experiment(self, experiment_id: str) -> bool:
        """Mark experiment as completed"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            experiment = self.experiments[experiment_id]
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            
            self._save_metadata()
            
            self.logger.info(f"Completed experiment: {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete experiment: {e}")
            return False
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID"""
        return self.experiments.get(experiment_id)
    
    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Experiment]:
        """List experiments with optional status filtering"""
        experiments = list(self.experiments.values())
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        
        return sorted(experiments, key=lambda x: x.created_at, reverse=True)

class ABTestManager:
    """Manage A/B tests for model versions"""
    
    def __init__(self, storage_path: str = "./ab_tests"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tests: Dict[str, ABTest] = {}
        self.metadata_file = self.storage_path / "ab_tests_metadata.json"
        self._load_metadata()
        self.logger.info("ABTestManager initialized successfully")
    
    def _load_metadata(self):
        """Load existing A/B test metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for test_id, test_data in data.items():
                        # Convert datetime strings back to datetime objects
                        test_data['created_at'] = datetime.fromisoformat(test_data['created_at'])
                        if test_data.get('started_at'):
                            test_data['started_at'] = datetime.fromisoformat(test_data['started_at'])
                        if test_data.get('ended_at'):
                            test_data['ended_at'] = datetime.fromisoformat(test_data['ended_at'])
                        test_data['status'] = ABTestStatus(test_data['status'])
                        self.tests[test_id] = ABTest(**test_data)
        except Exception as e:
            self.logger.error(f"Failed to load A/B test metadata: {e}")
    
    def _save_metadata(self):
        """Save A/B test metadata to disk"""
        try:
            data = {}
            for test_id, ab_test in self.tests.items():
                test_data = asdict(ab_test)
                test_data['created_at'] = ab_test.created_at.isoformat()
                if ab_test.started_at:
                    test_data['started_at'] = ab_test.started_at.isoformat()
                if ab_test.ended_at:
                    test_data['ended_at'] = ab_test.ended_at.isoformat()
                test_data['status'] = ab_test.status.value
                data[test_id] = test_data
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save A/B test metadata: {e}")
    
    def create_ab_test(self, name: str, description: str, control_version: str,
                      treatment_versions: List[str], traffic_split: Dict[str, float],
                      success_metrics: List[str]) -> str:
        """Create a new A/B test"""
        try:
            # Validate traffic split
            total_traffic = sum(traffic_split.values())
            if abs(total_traffic - 1.0) > 0.01:
                raise ValueError("Traffic split must sum to 1.0")
            
            test_id = str(uuid.uuid4())[:12]
            
            ab_test = ABTest(
                test_id=test_id,
                name=name,
                description=description,
                status=ABTestStatus.DRAFT,
                created_at=datetime.utcnow(),
                started_at=None,
                ended_at=None,
                control_version=control_version,
                treatment_versions=treatment_versions,
                traffic_split=traffic_split,
                success_metrics=success_metrics,
                results={},
                statistical_significance=None
            )
            
            self.tests[test_id] = ab_test
            self._save_metadata()
            
            self.logger.info(f"Created A/B test: {test_id} - {name}")
            return test_id
            
        except Exception as e:
            self.logger.error(f"Failed to create A/B test: {e}")
            raise
    
    def start_ab_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        try:
            if test_id not in self.tests:
                raise ValueError(f"A/B test not found: {test_id}")
            
            ab_test = self.tests[test_id]
            ab_test.status = ABTestStatus.ACTIVE
            ab_test.started_at = datetime.utcnow()
            
            self._save_metadata()
            
            self.logger.info(f"Started A/B test: {test_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start A/B test: {e}")
            return False
    
    def record_result(self, test_id: str, version: str, metric: str, value: float) -> bool:
        """Record a result for an A/B test"""
        try:
            if test_id not in self.tests:
                raise ValueError(f"A/B test not found: {test_id}")
            
            ab_test = self.tests[test_id]
            
            # Initialize results structure if needed
            if version not in ab_test.results:
                ab_test.results[version] = {}
            if metric not in ab_test.results[version]:
                ab_test.results[version][metric] = []
            
            # Add result
            ab_test.results[version][metric].append({
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self._save_metadata()
            
            self.logger.debug(f"Recorded result for A/B test {test_id}: {version}.{metric} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record A/B test result: {e}")
            return False
    
    def analyze_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and calculate statistical significance"""
        try:
            if test_id not in self.tests:
                raise ValueError(f"A/B test not found: {test_id}")
            
            ab_test = self.tests[test_id]
            results = ab_test.results
            
            if not results:
                return {"status": "no_data"}
            
            analysis = {
                "test_id": test_id,
                "status": ab_test.status.value,
                "versions_analyzed": list(results.keys()),
                "metrics_summary": {}
            }
            
            # Calculate summary statistics for each version and metric
            for version, version_results in results.items():
                analysis["metrics_summary"][version] = {}
                
                for metric, values in version_results.items():
                    if not values:
                        continue
                    
                    numeric_values = [v["value"] for v in values]
                    analysis["metrics_summary"][version][metric] = {
                        "count": len(numeric_values),
                        "mean": np.mean(numeric_values),
                        "std": np.std(numeric_values),
                        "min": np.min(numeric_values),
                        "max": np.max(numeric_values)
                    }
            
            # Simple statistical significance calculation (simplified t-test)
            if ab_test.control_version in results and len(ab_test.treatment_versions) > 0:
                significance_results = {}
                
                for metric in ab_test.success_metrics:
                    if (metric in results.get(ab_test.control_version, {}) and
                        any(metric in results.get(tv, {}) for tv in ab_test.treatment_versions)):
                        
                        control_values = [v["value"] for v in results[ab_test.control_version][metric]]
                        
                        for treatment_version in ab_test.treatment_versions:
                            if metric in results.get(treatment_version, {}):
                                treatment_values = [v["value"] for v in results[treatment_version][metric]]
                                
                                # Simple significance test (in production, use proper statistical tests)
                                if len(control_values) > 1 and len(treatment_values) > 1:
                                    control_mean = np.mean(control_values)
                                    treatment_mean = np.mean(treatment_values)
                                    
                                    # Simplified effect size
                                    effect_size = abs(treatment_mean - control_mean) / (control_mean + 1e-8)
                                    
                                    significance_results[f"{treatment_version}_vs_{ab_test.control_version}_{metric}"] = {
                                        "effect_size": effect_size,
                                        "significant": effect_size > 0.05  # 5% threshold
                                    }
                
                analysis["significance_tests"] = significance_results
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze A/B test results: {e}")
            return {"error": str(e)}
    
    def end_ab_test(self, test_id: str) -> bool:
        """End an A/B test"""
        try:
            if test_id not in self.tests:
                raise ValueError(f"A/B test not found: {test_id}")
            
            ab_test = self.tests[test_id]
            ab_test.status = ABTestStatus.COMPLETED
            ab_test.ended_at = datetime.utcnow()
            
            # Calculate final statistical significance
            analysis = self.analyze_results(test_id)
            if "significance_tests" in analysis:
                # Store overall significance (simplified)
                significances = [
                    test["significant"] for test in analysis["significance_tests"].values()
                ]
                ab_test.statistical_significance = sum(significances) / len(significances) if significances else 0
            
            self._save_metadata()
            
            self.logger.info(f"Ended A/B test: {test_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end A/B test: {e}")
            return False
    
    def get_ab_test(self, test_id: str) -> Optional[ABTest]:
        """Get A/B test by ID"""
        return self.tests.get(test_id)
    
    def list_ab_tests(self, status: Optional[ABTestStatus] = None) -> List[ABTest]:
        """List A/B tests with optional status filtering"""
        tests = list(self.tests.values())
        
        if status:
            tests = [t for t in tests if t.status == status]
        
        return sorted(tests, key=lambda x: x.created_at, reverse=True)

# Export classes for external use
__all__ = [
    'ModelStatus',
    'ExperimentStatus',
    'ABTestStatus',
    'ModelVersion',
    'Experiment',
    'ABTest',
    'ModelVersionManager',
    'ExperimentTracker',
    'ABTestManager'
]

logger.info("Versioning module loaded successfully")
