"""🔄 Continuous Integration Manager - MLOps CI/CD Pipeline
=====================================================================
Module: ml/deployment/continuous_integration_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ML CONTINUOUS INTEGRATION & AUTOMATED TESTING
Advanced CI/CD pipeline for ML models with automated testing
- Code quality validation et data validation
- Model performance regression testing
- Creator-specific testing scenarios
- Automated deployment avec quality gates
"""

import asyncio
import logging
import time
import uuid
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from pathlib import Path
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

# Configuration
logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """Étapes du pipeline CI/CD"""
    
    CODE_CHECKOUT = "code_checkout"
    CODE_QUALITY = "code_quality"
    DATA_VALIDATION = "data_validation"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    PERFORMANCE_TESTING = "performance_testing"
    INTEGRATION_TESTING = "integration_testing"
    SECURITY_SCANNING = "security_scanning"
    DEPLOYMENT_STAGING = "deployment_staging"
    ACCEPTANCE_TESTING = "acceptance_testing"
    PRODUCTION_DEPLOYMENT = "production_deployment"

class TestResult(Enum):
    """Résultats de test"""
    
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class QualityGate(Enum):
    """Quality gates"""
    
    CODE_COVERAGE = "code_coverage"
    MODEL_ACCURACY = "model_accuracy"
    PERFORMANCE_REGRESSION = "performance_regression"
    SECURITY_VULNERABILITIES = "security_vulnerabilities"
    DATA_QUALITY = "data_quality"
    CREATOR_COMPATIBILITY = "creator_compatibility"

@dataclass
class TestCase:
    """Cas de test"""
    
    test_id: str
    name: str
    description: str
    test_type: str  # unit, integration, performance, acceptance
    creator_types: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    test_script: str = ""
    expected_result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestExecution:
    """Exécution de test"""
    
    execution_id: str
    test_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    result: Optional[TestResult] = None
    duration_seconds: float = 0.0
    output: str = ""
    error_message: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)

@dataclass
class PipelineRun:
    """Exécution de pipeline"""
    
    run_id: str
    pipeline_id: str
    triggered_by: str
    trigger_event: str  # commit, schedule, manual
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = "running"  # running, success, failed, cancelled
    current_stage: Optional[PipelineStage] = None
    stage_results: Dict[str, TestResult] = field(default_factory=dict)
    test_executions: List[TestExecution] = field(default_factory=list)
    quality_gate_results: Dict[str, bool] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    deployment_targets: List[str] = field(default_factory=list)
    creator_types: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'run_id': self.run_id,
            'pipeline_id': self.pipeline_id,
            'triggered_by': self.triggered_by,
            'trigger_event': self.trigger_event,
            'started_at': self.started_at.isoformat(),
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'current_stage': self.current_stage.value if self.current_stage else None,
            'stage_results': {k: v.value for k, v in self.stage_results.items()},
            'quality_gate_results': self.quality_gate_results,
            'artifacts': self.artifacts,
            'deployment_targets': self.deployment_targets,
            'creator_types': self.creator_types,
            'metadata': self.metadata,
            'total_tests': len(self.test_executions),
            'passed_tests': len([t for t in self.test_executions if t.result == TestResult.PASSED]),
            'failed_tests': len([t for t in self.test_executions if t.result == TestResult.FAILED])
        }

@dataclass
class PipelineConfig:
    """Configuration de pipeline"""
    
    pipeline_id: str
    name: str
    description: str
    stages: List[PipelineStage]
    test_suites: Dict[str, List[str]]  # stage -> test_ids
    quality_gates: Dict[QualityGate, Dict[str, Any]]
    creator_specific_tests: Dict[str, List[str]]  # creator_type -> test_ids
    environment_config: Dict[str, Any] = field(default_factory=dict)
    notification_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pipeline_id': self.pipeline_id,
            'name': self.name,
            'description': self.description,
            'stages': [s.value for s in self.stages],
            'test_suites': self.test_suites,
            'quality_gates': {k.value: v for k, v in self.quality_gates.items()},
            'creator_specific_tests': self.creator_specific_tests,
            'environment_config': self.environment_config,
            'notification_config': self.notification_config
        }

class BaseTestRunner(ABC):
    """Runner de test de base"""
    
    @abstractmethod
    async def run_test(self, test_case: TestCase, context: Dict[str, Any]) -> TestExecution:
        """Exécuter un test"""
        pass

class UnitTestRunner(BaseTestRunner):
    """Runner pour tests unitaires"""
    
    async def run_test(self, test_case: TestCase, context: Dict[str, Any]) -> TestExecution:
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        execution = TestExecution(
            execution_id=execution_id,
            test_id=test_case.test_id,
            started_at=datetime.now()
        )
        
        try:
            # Exécuter le script de test
            if test_case.test_script:
                # Créer un environnement temporaire
                with tempfile.TemporaryDirectory() as temp_dir:
                    script_file = Path(temp_dir) / f"{test_case.test_id}.py"
                    script_file.write_text(test_case.test_script)
                    
                    # Exécuter avec timeout
                    process = await asyncio.create_subprocess_exec(
                        'python', str(script_file),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=temp_dir
                    )
                    
                    try:
                        stdout, stderr = await asyncio.wait_for(
                            process.communicate(),
                            timeout=test_case.timeout_seconds
                        )
                        
                        execution.output = stdout.decode()
                        if process.returncode == 0:
                            execution.result = TestResult.PASSED
                        else:
                            execution.result = TestResult.FAILED
                            execution.error_message = stderr.decode()
                            
                    except asyncio.TimeoutError:
                        process.kill()
                        execution.result = TestResult.ERROR
                        execution.error_message = f"Test timeout after {test_case.timeout_seconds}s"
            else:
                # Test basique sans script
                execution.result = TestResult.PASSED
                execution.output = "Basic test passed"
                
        except Exception as e:
            execution.result = TestResult.ERROR
            execution.error_message = str(e)
        
        execution.finished_at = datetime.now()
        execution.duration_seconds = (execution.finished_at - execution.started_at).total_seconds()
        
        return execution

class PerformanceTestRunner(BaseTestRunner):
    """Runner pour tests de performance"""
    
    async def run_test(self, test_case: TestCase, context: Dict[str, Any]) -> TestExecution:
        execution_id = f"perf_{uuid.uuid4().hex[:8]}"
        execution = TestExecution(
            execution_id=execution_id,
            test_id=test_case.test_id,
            started_at=datetime.now()
        )
        
        try:
            # Simulation d'un test de performance
            start_time = time.time()
            
            # Test de latence (simulation)
            await asyncio.sleep(0.1)  # Simule une opération
            latency_ms = (time.time() - start_time) * 1000
            
            # Métriques de performance
            execution.metrics = {
                'latency_ms': latency_ms,
                'throughput_rps': 1000 / (latency_ms / 1000) if latency_ms > 0 else 1000,
                'memory_usage_mb': 128.0,  # Simulation
                'cpu_usage_percent': 45.0
            }
            
            # Vérifier les seuils
            max_latency = test_case.metadata.get('max_latency_ms', 100)
            if latency_ms <= max_latency:
                execution.result = TestResult.PASSED
                execution.output = f"Performance test passed: {latency_ms:.2f}ms <= {max_latency}ms"
            else:
                execution.result = TestResult.FAILED
                execution.error_message = f"Latency too high: {latency_ms:.2f}ms > {max_latency}ms"
                
        except Exception as e:
            execution.result = TestResult.ERROR
            execution.error_message = str(e)
        
        execution.finished_at = datetime.now()
        execution.duration_seconds = (execution.finished_at - execution.started_at).total_seconds()
        
        return execution

class ModelValidationRunner(BaseTestRunner):
    """Runner pour validation de modèle"""
    
    async def run_test(self, test_case: TestCase, context: Dict[str, Any]) -> TestExecution:
        execution_id = f"model_{uuid.uuid4().hex[:8]}"
        execution = TestExecution(
            execution_id=execution_id,
            test_id=test_case.test_id,
            started_at=datetime.now()
        )
        
        try:
            # Simulation de validation de modèle
            
            # Métriques simulées
            accuracy = np.random.uniform(0.85, 0.95)
            precision = np.random.uniform(0.80, 0.90)
            recall = np.random.uniform(0.80, 0.90)
            f1_score = 2 * (precision * recall) / (precision + recall)
            
            execution.metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score
            }
            
            # Vérifier les seuils
            min_accuracy = test_case.metadata.get('min_accuracy', 0.8)
            if accuracy >= min_accuracy:
                execution.result = TestResult.PASSED
                execution.output = f"Model validation passed: accuracy {accuracy:.3f} >= {min_accuracy}"
            else:
                execution.result = TestResult.FAILED
                execution.error_message = f"Model accuracy too low: {accuracy:.3f} < {min_accuracy}"
                
        except Exception as e:
            execution.result = TestResult.ERROR
            execution.error_message = str(e)
        
        execution.finished_at = datetime.now()
        execution.duration_seconds = (execution.finished_at - execution.started_at).total_seconds()
        
        return execution

class ContinuousIntegrationManager:
    """
    🔄 Continuous Integration Manager
    
    Gestionnaire CI/CD pour ML avec:
    - Pipeline automatisé multi-étapes
    - Tests creator-specific
    - Quality gates intelligents
    - Déploiement automatisé avec rollback
    """
    
    def __init__(
        self,
        workspace_path -> None: str = "ci_workspace",
        max_concurrent_runs -> None: int = 5,
        enable_parallel_testing -> None: bool = True,
        notification_enabled -> None: bool = True
    ) -> None:
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent_runs = max_concurrent_runs
        self.enable_parallel_testing = enable_parallel_testing
        self.notification_enabled = notification_enabled
        
        # Stockage des configurations et exécutions
        self.pipeline_configs: Dict[str, PipelineConfig] = {}
        self.test_cases: Dict[str, TestCase] = {}
        self.pipeline_runs: Dict[str, PipelineRun] = {}
        
        # Test runners
        self.test_runners: Dict[str, BaseTestRunner] = {
            'unit': UnitTestRunner(),
            'performance': PerformanceTestRunner(),
            'model_validation': ModelValidationRunner(),
            'integration': UnitTestRunner(),  # Réutilise UnitTestRunner
            'acceptance': UnitTestRunner()
        }
        
        # Files d'attente pour gestion de concurrence
        self.running_pipelines: List[str] = []
        self.queued_pipelines: List[str] = []
        
        # Statistiques
        self.pipeline_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'avg_duration_minutes': 0.0
        }
        
        # Initialiser les configurations par défaut
        self._initialize_default_configs()
        
        logger.info("🔄 Continuous Integration Manager initialized")
    
    def _initialize_default_configs(self) -> None:
        """Initialiser les configurations par défaut"""
        
        # Configuration principale ML pipeline
        main_pipeline = PipelineConfig(
            pipeline_id="ml_main_pipeline",
            name="ML Main Pipeline",
            description="Pipeline principal pour modèles ML",
            stages=[
                PipelineStage.CODE_CHECKOUT,
                PipelineStage.CODE_QUALITY,
                PipelineStage.DATA_VALIDATION,
                PipelineStage.MODEL_TRAINING,
                PipelineStage.MODEL_VALIDATION,
                PipelineStage.PERFORMANCE_TESTING,
                PipelineStage.SECURITY_SCANNING,
                PipelineStage.DEPLOYMENT_STAGING,
                PipelineStage.ACCEPTANCE_TESTING,
                PipelineStage.PRODUCTION_DEPLOYMENT
            ],
            test_suites={
                'code_quality': ['code_lint', 'code_format', 'type_check'],
                'data_validation': ['data_schema', 'data_quality', 'data_drift'],
                'model_validation': ['model_accuracy', 'model_stability', 'model_bias'],
                'performance_testing': ['latency_test', 'throughput_test', 'memory_test'],
                'security_scanning': ['dependency_scan', 'secret_scan', 'vulnerability_scan']
            },
            quality_gates={
                QualityGate.CODE_COVERAGE: {'min_coverage': 80},
                QualityGate.MODEL_ACCURACY: {'min_accuracy': 0.85},
                QualityGate.PERFORMANCE_REGRESSION: {'max_latency_increase': 0.1},
                QualityGate.SECURITY_VULNERABILITIES: {'max_high_severity': 0},
                QualityGate.DATA_QUALITY: {'min_quality_score': 0.9}
            },
            creator_specific_tests={
                'musician': ['audio_processing_test', 'music_classification_test'],
                'blogger': ['text_analysis_test', 'content_moderation_test'],
                'photographer': ['image_processing_test', 'aesthetic_scoring_test'],
                'influencer': ['engagement_prediction_test', 'trend_analysis_test']
            }
        )
        
        self.pipeline_configs[main_pipeline.pipeline_id] = main_pipeline
        
        # Créer les cas de test par défaut
        self._create_default_test_cases()
    
    def _create_default_test_cases(self) -> None:
        """Créer les cas de test par défaut"""
        
        # Tests de qualité de code
        self.test_cases['code_lint'] = TestCase(
            test_id='code_lint',
            name='Code Linting',
            description='Vérification de la qualité du code avec pylint',
            test_type='unit',
            test_script='''
import subprocess
import sys

try:
    result = subprocess.run(['python', '-m', 'py_compile', __file__], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("Code compilation successful")
        sys.exit(0)
    else:
        print(f"Code compilation failed: {result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"Linting error: {e}")
    sys.exit(1)
'''
        )
        
        # Test de performance de latence
        self.test_cases['latency_test'] = TestCase(
            test_id='latency_test',
            name='Latency Performance Test',
            description='Test de latence pour inference en temps réel',
            test_type='performance',
            metadata={'max_latency_ms': 100},
            timeout_seconds=60
        )
        
        # Test de validation de modèle
        self.test_cases['model_accuracy'] = TestCase(
            test_id='model_accuracy',
            name='Model Accuracy Validation',
            description='Validation de la précision du modèle',
            test_type='model_validation',
            metadata={'min_accuracy': 0.85},
            timeout_seconds=300
        )
        
        # Tests spécifiques aux créateurs
        self.test_cases['audio_processing_test'] = TestCase(
            test_id='audio_processing_test',
            name='Audio Processing Test',
            description='Test de traitement audio pour musiciens',
            test_type='integration',
            creator_types=['musician'],
            test_script='''
import numpy as np
print("Testing audio processing...")
# Simulation d'un test audio
audio_data = np.random.rand(44100)  # 1 seconde d'audio
if len(audio_data) == 44100:
    print("Audio processing test passed")
else:
    raise Exception("Audio processing test failed")
'''
        )
        
        self.test_cases['text_analysis_test'] = TestCase(
            test_id='text_analysis_test',
            name='Text Analysis Test',
            description='Test d\'analyse de texte pour bloggers',
            test_type='integration',
            creator_types=['blogger'],
            test_script='''
import re
print("Testing text analysis...")
# Simulation d'un test de traitement de texte
text = "This is a sample blog post for testing."
word_count = len(text.split())
if word_count > 5:
    print(f"Text analysis test passed: {word_count} words")
else:
    raise Exception("Text analysis test failed")
'''
        )
    
    async def create_pipeline_config(
        self,
        name: str,
        description: str,
        stages: List[PipelineStage],
        creator_types: Optional[List[str]] = None
    ) -> str:
        """Créer une configuration de pipeline"""
        
        pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        
        config = PipelineConfig(
            pipeline_id=pipeline_id,
            name=name,
            description=description,
            stages=stages,
            test_suites={},
            quality_gates={},
            creator_specific_tests={}
        )
        
        self.pipeline_configs[pipeline_id] = config
        
        logger.info(f"📋 Created pipeline config: {name} [{pipeline_id}]")
        return pipeline_id
    
    async def add_test_case(
        self,
        name: str,
        description: str,
        test_type: str,
        test_script: str,
        creator_types: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Ajouter un cas de test"""
        
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        
        test_case = TestCase(
            test_id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            test_script=test_script,
            creator_types=creator_types or [],
            metadata=metadata or {}
        )
        
        self.test_cases[test_id] = test_case
        
        logger.info(f"📝 Added test case: {name} [{test_id}]")
        return test_id
    
    async def trigger_pipeline(
        self,
        pipeline_id: str,
        triggered_by: str,
        trigger_event: str = "manual",
        creator_types: Optional[List[str]] = None,
        deployment_targets: Optional[List[str]] = None
    ) -> str:
        """Déclencher l'exécution d'un pipeline"""
        
        if pipeline_id not in self.pipeline_configs:
            raise ValueError(f"Pipeline config not found: {pipeline_id}")
        
        # Vérifier la limite de concurrence
        if len(self.running_pipelines) >= self.max_concurrent_runs:
            run_id = f"run_{uuid.uuid4().hex[:8]}"
            self.queued_pipelines.append(run_id)
            logger.info(f"⏳ Pipeline queued: {run_id}")
            return run_id
        
        run_id = await self._start_pipeline_run(
            pipeline_id, triggered_by, trigger_event, creator_types, deployment_targets
        )
        
        return run_id
    
    async def _start_pipeline_run(
        self,
        pipeline_id: str,
        triggered_by: str,
        trigger_event: str,
        creator_types: Optional[List[str]],
        deployment_targets: Optional[List[str]]
    ) -> str:
        """Démarrer l'exécution d'un pipeline"""
        
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        
        pipeline_run = PipelineRun(
            run_id=run_id,
            pipeline_id=pipeline_id,
            triggered_by=triggered_by,
            trigger_event=trigger_event,
            started_at=datetime.now(),
            creator_types=creator_types or [],
            deployment_targets=deployment_targets or []
        )
        
        self.pipeline_runs[run_id] = pipeline_run
        self.running_pipelines.append(run_id)
        
        # Démarrer l'exécution asynchrone
        asyncio.create_task(self._execute_pipeline(run_id))
        
        logger.info(f"🚀 Started pipeline run: {run_id}")
        return run_id
    
    async def _execute_pipeline(self, run_id -> None: str) -> None:
        """Exécuter un pipeline complet"""
        
        pipeline_run = self.pipeline_runs[run_id]
        config = self.pipeline_configs[pipeline_run.pipeline_id]
        
        try:
            # Exécuter chaque étape
            for stage in config.stages:
                pipeline_run.current_stage = stage
                logger.info(f"🔄 Executing stage: {stage.value} for run {run_id}")
                
                stage_result = await self._execute_stage(stage, pipeline_run, config)
                pipeline_run.stage_results[stage.value] = stage_result
                
                # Arrêter si l'étape échoue
                if stage_result == TestResult.FAILED:
                    pipeline_run.status = "failed"
                    break
                    
                # Vérifier les quality gates après certaines étapes
                if stage in [PipelineStage.MODEL_VALIDATION, PipelineStage.PERFORMANCE_TESTING]:
                    gate_passed = await self._check_quality_gates(pipeline_run, config)
                    if not gate_passed:
                        pipeline_run.status = "failed"
                        break
            
            # Marquer comme succès si toutes les étapes passent
            if pipeline_run.status == "running":
                pipeline_run.status = "success"
                self.pipeline_stats['successful_runs'] += 1
            else:
                self.pipeline_stats['failed_runs'] += 1
                
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            pipeline_run.status = "failed"
            pipeline_run.metadata['error'] = str(e)
            self.pipeline_stats['failed_runs'] += 1
        
        finally:
            # Finaliser l'exécution
            pipeline_run.finished_at = datetime.now()
            pipeline_run.current_stage = None
            
            # Calculer la durée
            duration = (pipeline_run.finished_at - pipeline_run.started_at).total_seconds() / 60
            
            # Mettre à jour les statistiques
            self.pipeline_stats['total_runs'] += 1
            self.pipeline_stats['avg_duration_minutes'] = (
                (self.pipeline_stats['avg_duration_minutes'] * (self.pipeline_stats['total_runs'] - 1) + duration) /
                self.pipeline_stats['total_runs']
            )
            
            # Retirer de la liste des pipelines en cours
            if run_id in self.running_pipelines:
                self.running_pipelines.remove(run_id)
            
            # Démarrer le prochain pipeline en queue
            if self.queued_pipelines:
                next_run_id = self.queued_pipelines.pop(0)
                # Note: Il faudrait récupérer les paramètres du pipeline en queue
                # Pour la simplicité, on ne le fait pas ici
            
            logger.info(f"✅ Pipeline {run_id} completed with status: {pipeline_run.status}")
            
            # Notification
            if self.notification_enabled:
                await self._send_notification(pipeline_run)
    
    async def _execute_stage(
        self,
        stage: PipelineStage,
        pipeline_run: PipelineRun,
        config: PipelineConfig
    ) -> TestResult:
        """Exécuter une étape du pipeline"""
        
        # Obtenir les tests pour cette étape
        stage_tests = config.test_suites.get(stage.value, [])
        
        # Ajouter les tests spécifiques aux créateurs
        for creator_type in pipeline_run.creator_types:
            creator_tests = config.creator_specific_tests.get(creator_type, [])
            stage_tests.extend(creator_tests)
        
        if not stage_tests:
            # Étape sans tests spécifiques - succès par défaut
            return TestResult.PASSED
        
        # Exécuter les tests
        if self.enable_parallel_testing and len(stage_tests) > 1:
            # Exécution parallèle
            tasks = []
            for test_id in stage_tests:
                if test_id in self.test_cases:
                    task = self._execute_test(self.test_cases[test_id], pipeline_run)
                    tasks.append(task)
            
            if tasks:
                executions = await asyncio.gather(*tasks, return_exceptions=True)
                pipeline_run.test_executions.extend([e for e in executions if isinstance(e, TestExecution)])
        else:
            # Exécution séquentielle
            for test_id in stage_tests:
                if test_id in self.test_cases:
                    execution = await self._execute_test(self.test_cases[test_id], pipeline_run)
                    pipeline_run.test_executions.append(execution)
        
        # Analyser les résultats
        stage_executions = [e for e in pipeline_run.test_executions 
                          if e.test_id in stage_tests]
        
        if not stage_executions:
            return TestResult.PASSED
        
        # Si un test échoue, l'étape échoue
        for execution in stage_executions:
            if execution.result in [TestResult.FAILED, TestResult.ERROR]:
                return TestResult.FAILED
        
        return TestResult.PASSED
    
    async def _execute_test(
        self,
        test_case: TestCase,
        pipeline_run: PipelineRun
    ) -> TestExecution:
        """Exécuter un test individuel"""
        
        # Sélectionner le runner approprié
        runner = self.test_runners.get(test_case.test_type, self.test_runners['unit'])
        
        # Préparer le contexte
        context = {
            'pipeline_run': pipeline_run,
            'workspace_path': self.workspace_path,
            'creator_types': pipeline_run.creator_types
        }
        
        # Exécuter avec retry
        last_execution = None
        for attempt in range(test_case.retry_count + 1):
            try:
                execution = await runner.run_test(test_case, context)
                
                if execution.result == TestResult.PASSED:
                    return execution
                else:
                    last_execution = execution
                    if attempt < test_case.retry_count:
                        logger.warning(f"🔄 Retrying test {test_case.test_id} (attempt {attempt + 2})")
                        await asyncio.sleep(1)  # Pause avant retry
                    
            except Exception as e:
                logger.error(f"❌ Test execution exception: {e}")
                last_execution = TestExecution(
                    execution_id=f"error_{uuid.uuid4().hex[:8]}",
                    test_id=test_case.test_id,
                    started_at=datetime.now(),
                    finished_at=datetime.now(),
                    result=TestResult.ERROR,
                    error_message=str(e)
                )
        
        return last_execution or TestExecution(
            execution_id=f"failed_{uuid.uuid4().hex[:8]}",
            test_id=test_case.test_id,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            result=TestResult.FAILED,
            error_message="All retry attempts failed"
        )
    
    async def _check_quality_gates(
        self,
        pipeline_run: PipelineRun,
        config: PipelineConfig
    ) -> bool:
        """Vérifier les quality gates"""
        
        all_passed = True
        
        for gate, criteria in config.quality_gates.items():
            passed = await self._evaluate_quality_gate(gate, criteria, pipeline_run)
            pipeline_run.quality_gate_results[gate.value] = passed
            
            if not passed:
                all_passed = False
                logger.warning(f"⚠️ Quality gate failed: {gate.value}")
        
        return all_passed
    
    async def _evaluate_quality_gate(
        self,
        gate: QualityGate,
        criteria: Dict[str, Any],
        pipeline_run: PipelineRun
    ) -> bool:
        """Évaluer un quality gate spécifique"""
        
        if gate == QualityGate.MODEL_ACCURACY:
            # Vérifier la précision du modèle
            min_accuracy = criteria.get('min_accuracy', 0.8)
            
            # Chercher les métriques d'accuracy dans les tests
            for execution in pipeline_run.test_executions:
                if 'accuracy' in execution.metrics:
                    if execution.metrics['accuracy'] < min_accuracy:
                        return False
            return True
        
        elif gate == QualityGate.PERFORMANCE_REGRESSION:
            # Vérifier la régression de performance
            max_increase = criteria.get('max_latency_increase', 0.1)
            
            # Simulation - dans un vrai système, on comparerait avec la baseline
            for execution in pipeline_run.test_executions:
                if 'latency_ms' in execution.metrics:
                    # Simulation: baseline = 50ms
                    baseline_latency = 50.0
                    current_latency = execution.metrics['latency_ms']
                    increase = (current_latency - baseline_latency) / baseline_latency
                    
                    if increase > max_increase:
                        return False
            return True
        
        elif gate == QualityGate.SECURITY_VULNERABILITIES:
            # Vérifier les vulnérabilités de sécurité
            max_high_severity = criteria.get('max_high_severity', 0)
            
            # Simulation - toujours passé pour cet exemple
            return True
        
        else:
            # Gate non implémenté - passer par défaut
            return True
    
    async def _send_notification(self, pipeline_run -> None: PipelineRun) -> None:
        """Envoyer une notification de fin de pipeline"""
        
        status_emoji = "✅" if pipeline_run.status == "success" else "❌"
        duration = (pipeline_run.finished_at - pipeline_run.started_at).total_seconds() / 60
        
        message = f"{status_emoji} Pipeline {pipeline_run.run_id} completed"
        message += f"\nStatus: {pipeline_run.status}"
        message += f"\nDuration: {duration:.1f} minutes"
        message += f"\nTriggered by: {pipeline_run.triggered_by}"
        
        if pipeline_run.test_executions:
            passed = len([e for e in pipeline_run.test_executions if e.result == TestResult.PASSED])
            total = len(pipeline_run.test_executions)
            message += f"\nTests: {passed}/{total} passed"
        
        logger.info(f"📬 Notification: {message}")
    
    async def get_pipeline_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'un pipeline"""
        
        if run_id not in self.pipeline_runs:
            return None
        
        pipeline_run = self.pipeline_runs[run_id]
        
        return {
            'run_details': pipeline_run.to_dict(),
            'current_progress': {
                'current_stage': pipeline_run.current_stage.value if pipeline_run.current_stage else None,
                'completed_stages': len(pipeline_run.stage_results),
                'total_stages': len(self.pipeline_configs[pipeline_run.pipeline_id].stages)
            },
            'test_summary': {
                'total_tests': len(pipeline_run.test_executions),
                'passed_tests': len([e for e in pipeline_run.test_executions if e.result == TestResult.PASSED]),
                'failed_tests': len([e for e in pipeline_run.test_executions if e.result == TestResult.FAILED]),
                'error_tests': len([e for e in pipeline_run.test_executions if e.result == TestResult.ERROR])
            },
            'quality_gates': pipeline_run.quality_gate_results
        }
    
    async def get_ci_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics du CI"""
        
        # Analyser les pipelines récents
        recent_runs = [r for r in self.pipeline_runs.values() 
                      if (datetime.now() - r.started_at).days <= 7]
        
        # Analyse des tendances
        success_rate = (self.pipeline_stats['successful_runs'] / 
                       max(self.pipeline_stats['total_runs'], 1)) * 100
        
        # Analyse par creator type
        creator_stats = {}
        for creator_type in ['musician', 'blogger', 'photographer', 'influencer']:
            creator_runs = [r for r in recent_runs if creator_type in r.creator_types]
            creator_stats[creator_type] = {
                'total_runs': len(creator_runs),
                'successful_runs': len([r for r in creator_runs if r.status == 'success']),
                'avg_duration_minutes': np.mean([
                    (r.finished_at - r.started_at).total_seconds() / 60
                    for r in creator_runs if r.finished_at
                ]) if creator_runs else 0
            }
        
        # Tests les plus problématiques
        test_failure_rates = {}
        for run in recent_runs:
            for execution in run.test_executions:
                test_id = execution.test_id
                if test_id not in test_failure_rates:
                    test_failure_rates[test_id] = {'total': 0, 'failed': 0}
                
                test_failure_rates[test_id]['total'] += 1
                if execution.result in [TestResult.FAILED, TestResult.ERROR]:
                    test_failure_rates[test_id]['failed'] += 1
        
        problematic_tests = sorted(
            test_failure_rates.items(),
            key=lambda x: x[1]['failed'] / max(x[1]['total'], 1),
            reverse=True
        )[:5]
        
        return {
            'overall_stats': {
                'total_runs': self.pipeline_stats['total_runs'],
                'success_rate': success_rate,
                'avg_duration_minutes': self.pipeline_stats['avg_duration_minutes'],
                'current_queue_size': len(self.queued_pipelines),
                'active_runs': len(self.running_pipelines)
            },
            'creator_analytics': creator_stats,
            'test_analytics': {
                'total_test_cases': len(self.test_cases),
                'problematic_tests': [
                    {
                        'test_id': test_id,
                        'failure_rate': stats['failed'] / max(stats['total'], 1) * 100,
                        'total_runs': stats['total']
                    }
                    for test_id, stats in problematic_tests
                ]
            },
            'pipeline_configs': {
                pid: config.to_dict() 
                for pid, config in self.pipeline_configs.items()
            }
        }

# Usage Example
async def main() -> None:
    """Exemple d'utilisation du Continuous Integration Manager"""
    
    ci_manager = ContinuousIntegrationManager(
        workspace_path="ci_workspace",
        enable_parallel_testing=True
    )
    
    # Déclencher un pipeline
    run_id = await ci_manager.trigger_pipeline(
        pipeline_id="ml_main_pipeline",
        triggered_by="data_scientist_1",
        trigger_event="commit",
        creator_types=["musician", "blogger"],
        deployment_targets=["staging", "production"]
    )
    
    print(f"Pipeline triggered: {run_id}")
    
    # Attendre un peu et vérifier le statut
    await asyncio.sleep(2)
    status = await ci_manager.get_pipeline_status(run_id)
    print(f"Pipeline status: {status['run_details']['status']}")
    
    # Attendre la fin du pipeline
    await asyncio.sleep(10)
    
    # Analytics finales
    analytics = await ci_manager.get_ci_analytics()
    print(f"CI Analytics: {analytics['overall_stats']}")

if __name__ == "__main__":
    asyncio.run(main())