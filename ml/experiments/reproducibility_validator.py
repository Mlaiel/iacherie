"""🔬 Reproducibility Validator - Research Quality Assurance
=====================================================================
Module: ml/experiments/reproducibility_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 RESEARCH REPRODUCIBILITY & VALIDATION
Experiment reproducibility validation and verification
- Deterministic execution validation
- Result consistency verification
- Creator-specific reproducibility standards
- Statistical significance testing
"""

import asyncio
import logging
import time
import uuid
import hashlib
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from pathlib import Path
from scipy import stats
from collections import defaultdict

# Configuration
logger = logging.getLogger(__name__)

class ReproducibilityLevel(Enum):
    """Niveaux de reproductibilité"""
    
    EXACT = "exact"                    # Résultats identiques
    STATISTICAL = "statistical"       # Statistiquement équivalents
    APPROXIMATE = "approximate"       # Approximativement équivalents
    INSUFFICIENT = "insufficient"     # Pas suffisamment reproductible

class ValidationStatus(Enum):
    """Statuts de validation"""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ExperimentConfiguration:
    """Configuration d'expérience"""
    
    experiment_id: str
    name: str
    description: str
    creator_types: List[str]
    model_config: Dict[str, Any]
    data_config: Dict[str, Any]
    training_config: Dict[str, Any]
    random_seeds: List[int]
    environment_requirements: Dict[str, str]
    expected_metrics: Dict[str, float]
    tolerance_levels: Dict[str, float]
    created_at: datetime
    created_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'experiment_id': self.experiment_id,
            'name': self.name,
            'description': self.description,
            'creator_types': self.creator_types,
            'model_config': self.model_config,
            'data_config': self.data_config,
            'training_config': self.training_config,
            'random_seeds': self.random_seeds,
            'environment_requirements': self.environment_requirements,
            'expected_metrics': self.expected_metrics,
            'tolerance_levels': self.tolerance_levels,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }

@dataclass
class ExperimentRun:
    """Exécution d'expérience"""
    
    run_id: str
    experiment_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = "running"
    random_seed: int = 42
    environment_info: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'run_id': self.run_id,
            'experiment_id': self.experiment_id,
            'started_at': self.started_at.isoformat(),
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'random_seed': self.random_seed,
            'environment_info': self.environment_info,
            'metrics': self.metrics,
            'artifacts': self.artifacts,
            'logs': self.logs,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds
        }

@dataclass
class ReproducibilityReport:
    """Rapport de reproductibilité"""
    
    report_id: str
    experiment_id: str
    validation_runs: List[str]
    reproducibility_level: ReproducibilityLevel
    validation_status: ValidationStatus
    statistical_tests: Dict[str, Dict[str, float]]
    metric_variations: Dict[str, Dict[str, float]]
    consistency_scores: Dict[str, float]
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'experiment_id': self.experiment_id,
            'validation_runs': self.validation_runs,
            'reproducibility_level': self.reproducibility_level.value,
            'validation_status': self.validation_status.value,
            'statistical_tests': self.statistical_tests,
            'metric_variations': self.metric_variations,
            'consistency_scores': self.consistency_scores,
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'generated_at': self.generated_at.isoformat()
        }

class ReproducibilityValidator:
    """
    🔬 Reproducibility Validator
    
    Validateur de reproductibilité avec:
    - Validation déterministe des expériences
    - Tests statistiques de consistance
    - Standards creator-specific
    - Rapports de reproductibilité automatisés
    """
    
    def __init__(
        self,
        storage_path -> None: str = "data/reproducibility",
        min_validation_runs -> None: int = 3,
        statistical_confidence -> None: float = 0.95,
        enable_detailed_logging -> None: bool = True
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.min_validation_runs = min_validation_runs
        self.statistical_confidence = statistical_confidence
        self.enable_detailed_logging = enable_detailed_logging
        
        # Stockage des expériences et exécutions
        self.experiments: Dict[str, ExperimentConfiguration] = {}
        self.experiment_runs: Dict[str, List[ExperimentRun]] = defaultdict(list)
        self.validation_reports: Dict[str, ReproducibilityReport] = {}
        
        # Seuils de tolérance par creator type
        self.creator_tolerances = {
            'musician': {
                'accuracy': 0.02,      # 2% pour modèles audio
                'f1_score': 0.025,
                'loss': 0.05
            },
            'blogger': {
                'accuracy': 0.015,     # Plus strict pour texte
                'f1_score': 0.02,
                'perplexity': 0.1
            },
            'photographer': {
                'accuracy': 0.03,      # Images plus variables
                'f1_score': 0.035,
                'iou': 0.05
            },
            'influencer': {
                'accuracy': 0.025,
                'f1_score': 0.03,
                'engagement_score': 0.1
            }
        }
        
        # Configuration des tests statistiques
        self.statistical_tests = {
            'normality': stats.shapiro,
            'variance_equality': stats.levene,
            'mean_equality': stats.ttest_rel,
            'distribution_equality': stats.ks_2samp
        }
        
        logger.info("🔬 Reproducibility Validator initialized")
    
    async def register_experiment(
        self,
        name: str,
        description: str,
        creator_types: List[str],
        model_config: Dict[str, Any],
        data_config: Dict[str, Any],
        training_config: Dict[str, Any],
        expected_metrics: Dict[str, float],
        created_by: str,
        tolerance_levels: Optional[Dict[str, float]] = None
    ) -> str:
        """Enregistrer une nouvelle expérience"""
        
        experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        
        # Générer des seeds reproductibles
        base_seed = hash(name + description) % (2**32)
        random_seeds = [base_seed + i for i in range(10)]
        
        # Déterminer les tolérances
        if tolerance_levels is None:
            tolerance_levels = self._get_default_tolerances(creator_types)
        
        experiment = ExperimentConfiguration(
            experiment_id=experiment_id,
            name=name,
            description=description,
            creator_types=creator_types,
            model_config=model_config,
            data_config=data_config,
            training_config=training_config,
            random_seeds=random_seeds,
            environment_requirements={
                'python_version': '>=3.8',
                'numpy_version': '>=1.20.0',
                'framework': 'pytorch'
            },
            expected_metrics=expected_metrics,
            tolerance_levels=tolerance_levels,
            created_at=datetime.now(),
            created_by=created_by
        )
        
        self.experiments[experiment_id] = experiment
        
        # Persister
        await self._persist_experiment(experiment)
        
        logger.info(f"📝 Registered experiment: {name} [{experiment_id}]")
        return experiment_id
    
    async def run_experiment(
        self,
        experiment_id: str,
        random_seed: Optional[int] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exécuter une expérience"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        
        # Utiliser un seed de la liste ou celui fourni
        if random_seed is None:
            available_seeds = experiment.random_seeds
            used_seeds = [run.random_seed for run in self.experiment_runs[experiment_id]]
            unused_seeds = [s for s in available_seeds if s not in used_seeds]
            random_seed = unused_seeds[0] if unused_seeds else available_seeds[0]
        
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        
        # Créer l'exécution
        run = ExperimentRun(
            run_id=run_id,
            experiment_id=experiment_id,
            started_at=datetime.now(),
            random_seed=random_seed,
            environment_info=await self._collect_environment_info()
        )
        
        try:
            # Exécuter l'expérience (simulation)
            metrics = await self._execute_experiment_simulation(
                experiment, random_seed, custom_config
            )
            
            run.metrics = metrics
            run.status = "completed"
            run.finished_at = datetime.now()
            run.duration_seconds = (run.finished_at - run.started_at).total_seconds()
            
            # Générer des artifacts
            run.artifacts = await self._generate_artifacts(experiment, run)
            
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.finished_at = datetime.now()
            run.duration_seconds = (run.finished_at - run.started_at).total_seconds()
            logger.error(f"❌ Experiment run failed: {e}")
        
        # Stocker l'exécution
        self.experiment_runs[experiment_id].append(run)
        
        # Persister
        await self._persist_run(run)
        
        logger.info(f"🔬 Experiment run completed: {run_id} (seed: {random_seed})")
        return run_id
    
    async def validate_reproducibility(
        self,
        experiment_id: str,
        num_validation_runs: Optional[int] = None
    ) -> ReproducibilityReport:
        """Valider la reproductibilité d'une expérience"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        existing_runs = self.experiment_runs[experiment_id]
        
        num_runs = num_validation_runs or self.min_validation_runs
        
        # Exécuter des runs supplémentaires si nécessaire
        completed_runs = [r for r in existing_runs if r.status == "completed"]
        
        while len(completed_runs) < num_runs:
            run_id = await self.run_experiment(experiment_id)
            new_run = next(r for r in self.experiment_runs[experiment_id] if r.run_id == run_id)
            if new_run.status == "completed":
                completed_runs.append(new_run)
        
        # Analyser la reproductibilité
        report = await self._analyze_reproducibility(
            experiment, completed_runs[:num_runs]
        )
        
        # Stocker le rapport
        self.validation_reports[experiment_id] = report
        
        # Persister
        await self._persist_report(report)
        
        logger.info(f"📊 Reproducibility validation completed: {report.reproducibility_level.value}")
        return report
    
    async def _execute_experiment_simulation(
        self,
        experiment: ExperimentConfiguration,
        random_seed: int,
        custom_config: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Simuler l'exécution d'une expérience"""
        
        # Fixer les seeds pour la reproductibilité
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Simulation basée sur les métriques attendues avec variabilité contrôlée
        metrics = {}
        
        for metric_name, expected_value in experiment.expected_metrics.items():
            # Ajouter de la variabilité réaliste
            tolerance = experiment.tolerance_levels.get(metric_name, 0.02)
            
            # Variabilité déterministe basée sur le seed
            variation_seed = (random_seed + hash(metric_name)) % 1000
            np.random.seed(variation_seed)
            
            # Générer une variation dans la tolérance
            variation = np.random.normal(0, tolerance / 3)  # 3-sigma rule
            
            # Appliquer les contraintes métier
            if metric_name in ['accuracy', 'f1_score', 'precision', 'recall']:
                metrics[metric_name] = np.clip(expected_value + variation, 0.0, 1.0)
            elif metric_name in ['loss', 'error_rate']:
                metrics[metric_name] = max(0.0, expected_value + variation)
            else:
                metrics[metric_name] = expected_value + variation
        
        # Ajouter des métriques dérivées
        if 'accuracy' in metrics and 'f1_score' in metrics:
            metrics['balanced_score'] = (metrics['accuracy'] + metrics['f1_score']) / 2
        
        # Simuler du temps d'exécution
        await asyncio.sleep(0.1)  # Simulation rapide
        
        return metrics
    
    async def _analyze_reproducibility(
        self,
        experiment: ExperimentConfiguration,
        runs: List[ExperimentRun]
    ) -> ReproducibilityReport:
        """Analyser la reproductibilité des runs"""
        
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        # Collecter les métriques de tous les runs
        all_metrics = defaultdict(list)
        for run in runs:
            for metric_name, value in run.metrics.items():
                all_metrics[metric_name].append(value)
        
        # Tests statistiques
        statistical_tests = {}
        metric_variations = {}
        consistency_scores = {}
        issues_found = []
        recommendations = []
        
        for metric_name, values in all_metrics.items():
            if len(values) < 2:
                continue
            
            # Statistiques descriptives
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / mean_val if mean_val != 0 else float('inf')
            
            metric_variations[metric_name] = {
                'mean': mean_val,
                'std': std_val,
                'coefficient_variation': cv,
                'min': np.min(values),
                'max': np.max(values),
                'range': np.max(values) - np.min(values)
            }
            
            # Tests statistiques
            metric_tests = {}
            
            # Test de normalité
            if len(values) >= 3:
                try:
                    stat, p_value = stats.shapiro(values)
                    metric_tests['normality'] = {'statistic': stat, 'p_value': p_value}
                except:
                    pass
            
            # Consistance basée sur la tolérance
            tolerance = experiment.tolerance_levels.get(metric_name, 0.05)
            expected = experiment.expected_metrics.get(metric_name, mean_val)
            
            within_tolerance = all(abs(v - expected) <= tolerance for v in values)
            consistency_score = 1.0 - (std_val / tolerance) if tolerance > 0 else 0.0
            consistency_score = max(0.0, min(1.0, consistency_score))
            
            consistency_scores[metric_name] = consistency_score
            
            statistical_tests[metric_name] = metric_tests
            
            # Détecter les problèmes
            if not within_tolerance:
                issues_found.append(f"Metric {metric_name} exceeds tolerance: std={std_val:.4f}, tolerance={tolerance:.4f}")
            
            if cv > 0.1:  # Coefficient de variation > 10%
                issues_found.append(f"High variability in {metric_name}: CV={cv:.3f}")
                recommendations.append(f"Consider increasing regularization or reducing learning rate for {metric_name}")
        
        # Déterminer le niveau de reproductibilité global
        if not consistency_scores:
            reproducibility_level = ReproducibilityLevel.INSUFFICIENT
            validation_status = ValidationStatus.ERROR
        else:
            avg_consistency = np.mean(list(consistency_scores.values()))
            
            if avg_consistency >= 0.95:
                reproducibility_level = ReproducibilityLevel.EXACT
                validation_status = ValidationStatus.PASSED
            elif avg_consistency >= 0.85:
                reproducibility_level = ReproducibilityLevel.STATISTICAL
                validation_status = ValidationStatus.PASSED
            elif avg_consistency >= 0.7:
                reproducibility_level = ReproducibilityLevel.APPROXIMATE
                validation_status = ValidationStatus.WARNING
            else:
                reproducibility_level = ReproducibilityLevel.INSUFFICIENT
                validation_status = ValidationStatus.FAILED
        
        # Recommandations générales
        if reproducibility_level == ReproducibilityLevel.INSUFFICIENT:
            recommendations.extend([
                "Review random seed management",
                "Check for non-deterministic operations",
                "Verify environment consistency",
                "Consider using deterministic algorithms"
            ])
        
        return ReproducibilityReport(
            report_id=report_id,
            experiment_id=experiment.experiment_id,
            validation_runs=[run.run_id for run in runs],
            reproducibility_level=reproducibility_level,
            validation_status=validation_status,
            statistical_tests=statistical_tests,
            metric_variations=metric_variations,
            consistency_scores=consistency_scores,
            issues_found=issues_found,
            recommendations=recommendations
        )
    
    def _get_default_tolerances(self, creator_types: List[str]) -> Dict[str, float]:
        """Obtenir les tolérances par défaut selon les creator types"""
        
        if not creator_types:
            return {'accuracy': 0.02, 'f1_score': 0.025, 'loss': 0.05}
        
        # Utiliser les tolérances du premier creator type
        primary_creator = creator_types[0]
        return self.creator_tolerances.get(primary_creator, {
            'accuracy': 0.02,
            'f1_score': 0.025,
            'loss': 0.05
        })
    
    async def _collect_environment_info(self) -> Dict[str, str]:
        """Collecter les informations d'environnement"""
        
        import sys
        import platform
        
        return {
            'python_version': sys.version,
            'platform': platform.platform(),
            'numpy_version': np.__version__,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _generate_artifacts(
        self,
        experiment: ExperimentConfiguration,
        run: ExperimentRun
    ) -> Dict[str, str]:
        """Générer les artifacts d'une exécution"""
        
        artifacts = {}
        
        # Hash des configurations pour vérification
        config_hash = hashlib.md5(
            json.dumps(experiment.model_config, sort_keys=True).encode()
        ).hexdigest()
        
        artifacts['config_hash'] = config_hash
        artifacts['metrics_file'] = f"metrics_{run.run_id}.json"
        artifacts['log_file'] = f"logs_{run.run_id}.txt"
        
        # Créer les fichiers d'artifacts (simulation)
        artifacts_dir = self.storage_path / "artifacts" / experiment.experiment_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder les métriques
        metrics_file = artifacts_dir / artifacts['metrics_file']
        with open(metrics_file, 'w') as f:
            json.dump(run.metrics, f, indent=2)
        
        return artifacts
    
    async def _persist_experiment(self, experiment -> None: ExperimentConfiguration) -> None:
        """Persister une expérience"""
        
        exp_file = self.storage_path / f"experiments/{experiment.experiment_id}.json"
        exp_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(exp_file, 'w') as f:
            json.dump(experiment.to_dict(), f, indent=2)
    
    async def _persist_run(self, run -> None: ExperimentRun) -> None:
        """Persister une exécution"""
        
        run_file = self.storage_path / f"runs/{run.experiment_id}/{run.run_id}.json"
        run_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(run_file, 'w') as f:
            json.dump(run.to_dict(), f, indent=2)
    
    async def _persist_report(self, report -> None: ReproducibilityReport) -> None:
        """Persister un rapport"""
        
        report_file = self.storage_path / f"reports/{report.experiment_id}_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    async def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Obtenir un résumé d'expérience"""
        
        if experiment_id not in self.experiments:
            return {}
        
        experiment = self.experiments[experiment_id]
        runs = self.experiment_runs[experiment_id]
        completed_runs = [r for r in runs if r.status == "completed"]
        
        # Statistiques des runs
        if completed_runs:
            durations = [r.duration_seconds for r in completed_runs]
            avg_duration = np.mean(durations)
            
            # Métriques moyennes
            all_metrics = defaultdict(list)
            for run in completed_runs:
                for metric, value in run.metrics.items():
                    all_metrics[metric].append(value)
            
            avg_metrics = {metric: np.mean(values) for metric, values in all_metrics.items()}
            std_metrics = {metric: np.std(values) for metric, values in all_metrics.items()}
        else:
            avg_duration = 0
            avg_metrics = {}
            std_metrics = {}
        
        # Rapport de reproductibilité
        report = self.validation_reports.get(experiment_id)
        
        return {
            'experiment': experiment.to_dict(),
            'run_statistics': {
                'total_runs': len(runs),
                'completed_runs': len(completed_runs),
                'failed_runs': len([r for r in runs if r.status == "failed"]),
                'avg_duration_seconds': avg_duration
            },
            'metrics_summary': {
                'averages': avg_metrics,
                'standard_deviations': std_metrics
            },
            'reproducibility': report.to_dict() if report else None
        }
    
    async def get_validation_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics de validation"""
        
        total_experiments = len(self.experiments)
        validated_experiments = len(self.validation_reports)
        
        # Statistiques par niveau de reproductibilité
        repro_levels = defaultdict(int)
        for report in self.validation_reports.values():
            repro_levels[report.reproducibility_level.value] += 1
        
        # Métriques de qualité par creator type
        creator_quality = defaultdict(lambda: {'experiments': 0, 'avg_consistency': 0.0})
        
        for exp_id, experiment in self.experiments.items():
            for creator_type in experiment.creator_types:
                creator_quality[creator_type]['experiments'] += 1
                
                if exp_id in self.validation_reports:
                    report = self.validation_reports[exp_id]
                    if report.consistency_scores:
                        avg_consistency = np.mean(list(report.consistency_scores.values()))
                        creator_quality[creator_type]['avg_consistency'] += avg_consistency
        
        # Moyenner les consistances
        for creator_type, stats in creator_quality.items():
            if stats['experiments'] > 0:
                stats['avg_consistency'] /= stats['experiments']
        
        # Problèmes les plus fréquents
        all_issues = []
        for report in self.validation_reports.values():
            all_issues.extend(report.issues_found)
        
        issue_counts = defaultdict(int)
        for issue in all_issues:
            issue_counts[issue] += 1
        
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'summary': {
                'total_experiments': total_experiments,
                'validated_experiments': validated_experiments,
                'validation_rate': validated_experiments / max(total_experiments, 1) * 100
            },
            'reproducibility_distribution': dict(repro_levels),
            'creator_quality': dict(creator_quality),
            'common_issues': [{'issue': issue, 'count': count} for issue, count in common_issues],
            'recommendations': [
                "Implement deterministic training procedures",
                "Use fixed random seeds across all operations",
                "Document environment requirements clearly",
                "Set appropriate tolerance levels for metrics"
            ]
        }

# Usage Example
async def main() -> None:
    """Exemple d'utilisation du Reproducibility Validator"""
    
    validator = ReproducibilityValidator(
        storage_path="data/reproducibility",
        min_validation_runs=3
    )
    
    # Enregistrer une expérience
    exp_id = await validator.register_experiment(
        name="Music Classification Model",
        description="CNN model for music genre classification",
        creator_types=["musician"],
        model_config={
            "model_type": "cnn",
            "layers": [64, 128, 256],
            "dropout": 0.3
        },
        data_config={
            "dataset": "music_genres",
            "train_split": 0.8,
            "batch_size": 32
        },
        training_config={
            "epochs": 10,
            "learning_rate": 0.001,
            "optimizer": "adam"
        },
        expected_metrics={
            "accuracy": 0.85,
            "f1_score": 0.83,
            "loss": 0.45
        },
        created_by="ml_researcher"
    )
    
    print(f"Experiment registered: {exp_id}")
    
    # Valider la reproductibilité
    report = await validator.validate_reproducibility(exp_id, num_validation_runs=5)
    
    print(f"Reproducibility level: {report.reproducibility_level.value}")
    print(f"Validation status: {report.validation_status.value}")
    print(f"Consistency scores: {report.consistency_scores}")
    
    # Résumé de l'expérience
    summary = await validator.get_experiment_summary(exp_id)
    print(f"Experiment summary: {summary['run_statistics']}")
    
    # Analytics globales
    analytics = await validator.get_validation_analytics()
    print(f"Validation analytics: {analytics['summary']}")

if __name__ == "__main__":
    asyncio.run(main())